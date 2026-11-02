# frozen_string_literal: true
require_relative 'actor_markov_joint'
require_relative 'empirical_group_baseline'
require 'json'
module RithmP2R6FromModels
 module_function
 def run(path, draws:20_000, seed:20261102)
  actor=RithmActorMarkov.evaluate(path)
  oracle=RithmEmpiricalBaseline.evaluate(path)
  by_session=oracle.fetch(:session_rows).to_h{|r|[r.fetch(:session),r]}
  paired=actor.fetch(:sessions_detail).map do |r|
   other=by_session.fetch(r.fetch(:session))
   raise 'different session count' unless r.fetch(:n)==other.fetch(:n)
   {session:r[:session],n:r[:n],
    joint:r[:joint]-other.fetch('conditional').fetch(:joint),
    count:r[:count]-other.fetch('conditional').fetch(:count)}
  end
  raise 'source mismatch' unless paired.size==24 && paired.sum{|r|r[:n]}==5616
  stats=[:joint,:count].to_h do |head|
   [head,[:equal_session,:transition_weighted].to_h do |estimand|
    weighted=estimand==:transition_weighted
    mean=->(v){v.sum{|r|r[head]*(weighted ? r[:n] : 1)}/v.sum{|r|weighted ? r[:n] : 1}.to_f}
    rng=Random.new(seed)
    b=Array.new(draws){v=Array.new(paired.size){paired.fetch(rng.rand(paired.size))};mean.call(v)}.sort
    [estimand,{point:mean.call(paired),lower:b[(draws*0.025).floor],upper:b[(draws*0.975).floor]}]
   end]
  end
  {n:5616,sessions:24,paired:paired,stats:stats}
 end
end
puts JSON.pretty_generate(RithmP2R6FromModels.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
