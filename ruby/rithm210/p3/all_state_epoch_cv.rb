# frozen_string_literal: true
# P3-R16B: all 5,616 group transitions, preserving the P3-R14 train-only
# sixfold actor Markov / epoch20 model. Aggregate-only outputs; source SHA sealed.
require_relative 'epoch_independent_welfare'
require 'json'
module Rithm210AllStateEpochCV
  module_function
  E=Rithm210EpochIndependentWelfare
  O=Rithm210OnlineIdentity
  def convolve(ps)
    ps.reduce([1.0]) do |prev,p|
      raise 'invalid forecast probability' unless p.between?(0.0,1.0)
      out=Array.new(prev.size+1,0.0)
      prev.each_with_index{|v,i|out[i]+=v*(1-p);out[i+1]+=v*p}
      out
    end
  end
  def group_score(people,ps)
    raise 'six people/probabilities required' unless people.size==6 && ps.size==6
    a=people.each_with_index.select{|r,i|r['RouteA'].to_i==1}
    b=people.each_with_index.select{|r,i|r['RouteA'].to_i==0}
    n=a.size
    raise 'source occupancy mismatch' unless n==people.first['NumA'].to_i && a.size+b.size==6
    pa=a.map{|r,i|ps[i]};pb=b.map{|r,i|ps[i]}
    d=a.sum{|r,i|r['switchAtoBWill'].to_i}
    u=b.sum{|r,i|r['switchBtoAWill'].to_i}
    raise 'source next-occupancy mismatch' unless n+u-d==people.first['NumAnext'].to_i
    pd=convolve(pa);pu=convolve(pb)
    joint=pu[u]*pd[d]
    count=pu.each_with_index.sum{|v,i|pd.each_with_index.sum{|w,j|i-j==u-d ? v*w : 0.0}}
    raise 'zero event likelihood' unless joint>0 && count>0
    mean=n+pb.sum-pa.sum
    variance=ps.sum{|p|p*(1-p)}
    expected=3*((mean-4)**2+variance)
    exact=pu.each_with_index.sum{|v,i|pd.each_with_index.sum{|w,j|3*(n+i-j-4)**2*v*w}}
    raise 'quadratic welfare convolution mismatch' unless (expected-exact).abs<1e-8
    actual=3*(n+u-d-4)**2
    {joint:-Math.log(joint),count:-Math.log(count),forecast_excess:expected,
     actual_excess:actual,error:actual-expected,gross_pred:ps.sum,
     gross_actual:u+d,zero_pred:pu[0]*pd[0],zero_actual:u+d==0 ? 1.0 : 0.0,
     cancel_pred:(1..[n,6-n].min).sum{|k|pu[k]*pd[k]},cancel_actual:u==d && u>0 ? 1.0 : 0.0}
  end
  def run(csv)
    raise 'original CSV SHA mismatch' unless Digest::SHA256.file(csv).hexdigest==E::SHA
    groups=O.source(csv);sessions=groups.keys.map(&:first).uniq.sort
    raise '24-session invariant violated' unless sessions.size==24
    fold=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    rows=[]
    6.times do |f|
      held=sessions.select{|s|fold[s]==f}
      basefit=O.train(groups,held)
      tally=E.train_epoch(groups,held)
      groups.each do |(s,section,g,t),people|
        next unless fold[s]==f
        base=people.map{|r|O.probability(basefit,r)}
        epoch=people.each_with_index.map{|r,i|E.probability(base[i],tally,r,t)}
        {markov:base,epoch20:epoch}.each do |model,ps|
          rows<<{session:s,trt:people.first['trt'].to_i,n:people.first['NumA'].to_i,
                 epoch:E.epoch(t),model:model,metrics:group_score(people,ps)}
        end
      end
    end
    raise '2 x 5616 scored groups required' unless rows.size==11_232
    dims={overall:[],by_treatment:[:trt],by_occupancy:[:n],by_treatment_epoch:[:trt,:epoch]}
    agg=dims.to_h do |name,fields|
      [name,rows.group_by{|r|[*fields.map{|k|r[k]},r[:model]]}.map do |label,subset|
        {strata:label,n:subset.size,**subset.first[:metrics].keys.to_h{|metric|
          [metric,subset.sum{|r|r[:metrics][metric]}/subset.size.to_f]}}
      end.sort_by{|r|r[:strata].map(&:to_s)}]
    end
    {sessions:sessions.size,groups:groups.size,model_count:2,**agg,
     limitation:'same-source exploratory 6fold session holdout, not a generative 40-period path forecast or causal intervention'}
  end
end
puts JSON.pretty_generate(Rithm210AllStateEpochCV.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
