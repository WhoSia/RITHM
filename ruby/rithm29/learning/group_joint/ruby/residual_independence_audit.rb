# frozen_string_literal: true
require_relative 'actor_markov_joint'
require 'json'
module RithmResidualAudit
 module_function
 def cross_residual(u,d,eu,ed);(u-eu)*(d-ed);end
 def execute(path, draws:20_000, seed:20261102)
  groups=RithmActorMarkov.read_groups(path)
  sessions=groups.keys.map(&:first).uniq.sort
  folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
  records=[]
  6.times do |f|
   fit=RithmActorMarkov.trained(groups,folds,f)
   groups.each do |(s,section,g,t),members|
    next unless folds[s]==f
    pa=members.select{|r|r['RouteA'].to_i==1}.map{|r|RithmActorMarkov.p_switch(fit,r)}
    pb=members.select{|r|r['RouteA'].to_i==0}.map{|r|RithmActorMarkov.p_switch(fit,r)}
    d=members.sum{|r|r['switchAtoBWill'].to_i}
    u=members.sum{|r|r['switchBtoAWill'].to_i}
    ed=pa.sum;eu=pb.sum
    records<<{session:s,cross:cross_residual(u,d,eu,ed),ru:u-eu,rd:d-ed}
   end
  end
  raise 'count mismatch' unless records.size==5616 && sessions.size==24
  mean=->(a,k){a.sum{|r|r[k]}/a.size}
  by=sessions.map{|s|a=records.select{|r|r[:session]==s};{session:s,n:a.size,cross:mean.call(a,:cross),ru:mean.call(a,:ru),rd:mean.call(a,:rd)}}
  result={sessions:24,transitions:5616,pooled:{}}
  [:cross,:ru,:rd].each do |key|
   rng=Random.new(seed)
   samples=Array.new(draws) do
    resampled=Array.new(by.size){by.fetch(rng.rand(by.size))}
    resampled.sum{|r|r[:n]*r[key]}/resampled.sum{|r|r[:n]}.to_f
   end.sort
   result[:pooled][key]={point:mean.call(records,key),lower:samples[(draws*0.025).floor],upper:samples[(draws*0.975).floor]}
  end
  result
 end
end
puts JSON.pretty_generate(RithmResidualAudit.execute(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
