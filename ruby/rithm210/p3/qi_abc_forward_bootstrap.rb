# frozen_string_literal: true
# R16F: paired full-session bootstrap of actual 40-round *autonomous*
# model trajectories, not 39 repeated observed-state conditional predictions.
require_relative 'qi_abc_forward_trajectory'
require 'json'
module Rithm210QiABCForwardBootstrap
  module_function
  F=Rithm210QiABCForwardTrajectory
  PAIRS={epoch20_minus_markov:[:epoch20,:markov],
         epoch20_minus_qi_a:[:epoch20,:a],
         qi_c_minus_qi_a:[:c,:a],
         qi_b_minus_qi_c:[:b,:c]}.freeze
  METRICS=[:absolute_error,:squared_error,:terminal_logloss].freeze
  def bootstrap(sessions,rows,draws:20_000,seed:20261105)
    raise ArgumentError,'sessions and positive draws required' if sessions.empty? || !draws.positive?
    rng=Random.new(seed)
    METRICS.to_h do |metric|
      comparisons=PAIRS.to_h do |label,(first,second)|
        by=sessions.map do |s|
          x=rows.fetch(first).select{|r|r[:session]==s}
          y=rows.fetch(second).select{|r|r[:session]==s}
          raise 'missing paired session trajectory' unless x.size==y.size && x.size>0
          [x.size,x.sum{|r|r.fetch(metric)}-y.sum{|r|r.fetch(metric)}]
        end
        n=by.sum(&:first)
        point=by.sum(&:last)/n.to_f
        replicates=[]
        draws.times do
          sample=Array.new(sessions.size){by.fetch(rng.rand(sessions.size))}
          denom=sample.sum(&:first)
          replicates<<sample.sum(&:last)/denom.to_f
        end
        replicates.sort!
        [label,{n:n,delta:point,
          percentile95:[replicates.fetch((replicates.size*0.025).floor),
                        replicates.fetch((replicates.size*0.975).floor)]}]
      end
      [metric,comparisons]
    end
  end
  def run(path)
    sessions,rows=F.source_rows(path)
    {sessions:sessions.size,complete_paths:48,replicates:20_000,
     results:bootstrap(sessions,rows),
     limitation:'Repeated within-source exploration; only 48 complete paths clustered in 24 sessions; fixed train-fold fits, no parameter-refit or external causal identification.'}
  end
end
puts JSON.pretty_generate(Rithm210QiABCForwardBootstrap.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
