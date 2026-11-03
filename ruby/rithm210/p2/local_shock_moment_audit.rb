# frozen_string_literal: true
# P2-R3 source-based heldout diagnostic. Gamma is FIXED; no heldout tuning.
require_relative 'residual_negative_control'
require 'json'
module Rithm210LocalShockMomentAudit
  module_function
  def shifted(p,shift)
    x=Math.log(p/(1-p))+shift
    1.0/(1.0+Math.exp(-x))
  end
  def predicted_cross(pa,pb,gamma)
    eu=pb.sum; ed=pa.sum
    [-gamma,gamma].sum do |z|
      (pb.sum{|p|shifted(p,z)}-eu)*(pa.sum{|p|shifted(p,z)}-ed)
    end/2.0
  end
  def study(path,gamma:0.30,draws:4_000,seed:20261103)
    m=Rithm210ResidualNegativeControl
    groups=m.read_groups(path)
    sessions=groups.keys.map(&:first).uniq.sort
    folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    records=[]
    6.times do |fold|
      fit=m.fit(groups,folds,fold)
      groups.each do |(s,section,g,period),people|
        next unless folds[s]==fold
        pa=people.select{|r|r['RouteA'].to_i==1}.map{|r|m.probability(fit,r)}
        pb=people.select{|r|r['RouteA'].to_i==0}.map{|r|m.probability(fit,r)}
        u=people.sum{|r|r['switchBtoAWill'].to_i}
        d=people.sum{|r|r['switchAtoBWill'].to_i}
        ru=u-pb.sum;rd=d-pa.sum
        records<<{session:s,section:section,group:g,period:period,
          within:ru*rd,model:predicted_cross(pa,pb,gamma),ru:ru,rd:rd}
      end
    end
    matched=records.group_by{|r|[r[:session],r[:section],r[:period]]}.values.flat_map do |set|
      set.flat_map do |r|
        other=set.reject{|q|q[:group]==r[:group]}
        next [] if other.empty?
        [{session:r[:session],observed:r[:within],predicted:r[:model],
          between:r[:ru]*other.sum{|q|q[:rd]}/other.size.to_f}]
      end
    end
    raise 'group count mismatch' unless records.size==5616 && matched.size==5148
    average=->(a,k){a.sum{|r|r[k]}/a.size.to_f}
    by=matched.group_by{|r|r[:session]}.map do |s,a|
      {session:s,n:a.size,
        excess:average.call(a,:observed)-average.call(a,:between),
        predicted:average.call(a,:predicted),
        remaining:average.call(a,:observed)-average.call(a,:between)-average.call(a,:predicted)}
    end
    interval=->(key){
      rng=Random.new(seed);n=by.size
      samples=Array.new(draws) do
        ss=Array.new(n){by.fetch(rng.rand(n))}
        ss.sum{|r|r[key]*r[:n]}/ss.sum{|r|r[:n]}.to_f
      end.sort
      {point:by.sum{|r|r[key]*r[:n]}/by.sum{|r|r[:n]}.to_f,
        lower:samples[(draws*0.025).floor],upper:samples[(draws*0.975).floor]}
    }
    {gamma:gamma,scored:records.size,matched:matched.size,
      overall_observed_within:average.call(records,:within),
      overall_model_within:average.call(records,:model),
      matched_observed_within:average.call(matched,:observed),
      matched_observed_between:average.call(matched,:between),
      matched_model_within:average.call(matched,:predicted),
      session_bootstrap:{excess:interval.call(:excess),
        model_explained:interval.call(:predicted),remaining:interval.call(:remaining)}}
  end
end
if __FILE__==$PROGRAM_NAME
  puts JSON.pretty_generate(Rithm210LocalShockMomentAudit.study(ARGV.fetch(0),
    gamma:Float(ARGV.fetch(1,'0.30')),draws:Integer(ARGV.fetch(2,'4000'))))
end
