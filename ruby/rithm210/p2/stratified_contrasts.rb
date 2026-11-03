# frozen_string_literal: true
# Paired within-session descriptive contrasts; gamma already frozen at .30.
require_relative 'treatment_epoch_cv'
module Rithm210StratifiedContrasts
  module_function
  def average(rows)
    rows.sum{|r|r.fetch(:joint1)-r.fetch(:joint0)}/rows.size.to_f
  end
  def construct(rows)
    sessions=rows.map{|r|r[:session]}.uniq.sort
    sessions.map do |s|
      rr=rows.select{|r|r[:session]==s}
      grouped=rr.group_by{|r|[r[:treatment],r[:epoch]]}
      raise 'missing stratum' unless (1..3).all?{|t|%w[early middle late].all?{|ep|grouped[[t,ep]]&.any?}}
      trt=(1..3).to_h{|t|[t,average(rr.select{|r|r[:treatment]==t})]}
      ep=%w[early middle late].to_h{|e|[e,average(rr.select{|r|r[:epoch]==e})]}
      {session:s,full_minus_no:trt[3]-trt[1],
        partial_minus_no:trt[2]-trt[1],
        early_minus_late:ep['early']-ep['late'],
        full_early_minus_late:average(grouped[[3,'early']])-average(grouped[[3,'late']]),
        interaction_full_no_early_late:
          (average(grouped[[3,'early']])-average(grouped[[3,'late']]))-
          (average(grouped[[1,'early']])-average(grouped[[1,'late']]))}
    end
  end
  def interval(sessions,metric,draws:20_000,seed:20261103)
    rng=Random.new(seed)
    n=sessions.size
    estimate=->(a){a.sum{|r|r.fetch(metric)}/a.size.to_f}
    draws_array=Array.new(draws){estimate.call(Array.new(n){sessions.fetch(rng.rand(n))})}.sort
    {point:estimate.call(sessions),lower:draws_array[(draws*0.025).floor],
      upper:draws_array[(draws*0.975).floor]}
  end
  def report(path,draws:20_000)
    rows=Rithm210TreatmentEpochCV.predict(Rithm210ResidualNegativeControl.read_groups(path))
    sessions=construct(rows)
    {n_groups:rows.size,sessions:sessions.size,
      contrasts:(sessions.first.keys-[:session]).to_h{|metric|[metric,interval(sessions,metric,draws:draws)]}}
  end
end
puts JSON.pretty_generate(Rithm210StratifiedContrasts.report(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
