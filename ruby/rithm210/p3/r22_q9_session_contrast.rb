# frozen_string_literal: true
# R22: session-equal paired exploratory forecast contrasts from aggregate JSON.
# Never read or publish participant rows. 24 session clusters, not 5760 iid.
require 'json'
module Rithm210R22Q9SessionContrast
  module_function
  METRICS=[:logloss,:brier,:cost_abs_error].freeze
  PAIRS=[['persistent_q9','frequency'],['persistent_q9','persistent_q3'],
         ['uniform_q9','uniform_q3']].freeze

  def compare(session_rows,treatment:,candidate:,baseline:,draws:20_000,seed:20261106)
    raise ArgumentError,'positive bootstrap draws' unless draws.is_a?(Integer)&&draws.positive?
    rows=session_rows.select{|r|r.fetch(:treatment)==treatment}
    a=rows.select{|r|r.fetch(:model).to_s==candidate}
    b=rows.select{|r|r.fetch(:model).to_s==baseline}
    a_by=a.to_h{|r|[r.fetch(:session),r]}
    b_by=b.to_h{|r|[r.fetch(:session),r]}
    raise ArgumentError,'duplicate or unpaired sessions' unless
      a_by.size==a.size&&b_by.size==b.size&&a_by.keys.sort==b_by.keys.sort&&a_by.size>=2
    ids=a_by.keys.sort
    raise ArgumentError,'different group observation support' unless ids.all?{|s|a_by[s][:groups]==b_by[s][:groups]}
    metrics=METRICS.to_h do |key|
      values=ids.map{|s|a_by.fetch(s).fetch(key)-b_by.fetch(s).fetch(key)}
      rng=Random.new(seed)
      draws_sorted=Array.new(draws) do
        Array.new(ids.size){values[rng.rand(ids.size)]}.sum/ids.size.to_f
      end.sort
      [key,{mean_difference:values.sum/ids.size.to_f,
        percentile95:[draws_sorted[(draws*.025).floor],draws_sorted[(draws*.975).floor]],
        candidate_better_sessions:values.count{|d|d<0}}]
    end
    {treatment:treatment,candidate:candidate,baseline:baseline,sessions:ids.size,
     metrics:metrics,note:'Exploratory whole-session resampling of repeatedly investigated source.'}
  end

  def run(path,draws:20_000)
    source=JSON.parse(File.read(path),symbolize_names:true)
    raise ArgumentError,'original coverage required' unless source[:sessions]==24&&source[:groups]==5760
    rows=source.fetch(:session_results)
    raise 'expected 360 session-treatment-model cells' unless rows.size==24*3*5
    (1..3).flat_map do |trt|
      PAIRS.map{|cand,base|compare(rows,treatment:trt,candidate:cand,
        baseline:base,draws:draws)}
    end
  end
end
puts JSON.pretty_generate(Rithm210R22Q9SessionContrast.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
