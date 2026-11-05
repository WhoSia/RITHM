# frozen_string_literal: true
# Qi et al. Part I (2023) Model A structural equation, plus Part II (2024)
# independent individual switch aggregation. Transfer to DIFFERENT full-info experiment.
require_relative 'all_state_epoch_cv'
require 'digest'
require 'json'
module Rithm210QiModelATransfer
  module_function
  E=Rithm210EpochIndependentWelfare
  O=Rithm210OnlineIdentity
  M=Rithm210AllStateEpochCV
  def sigmoid(z)
    return 1.0/(1.0+Math.exp(-z)) if z>=0
    v=Math.exp(z);v/(1+v)
  end
  def switch_probability(params,route,n)
    eta_a,eta_b,theta=params
    raise ArgumentError,'invalid parameters' unless eta_a.between?(0,1) && eta_b.between?(0,1) && theta>0 && (0..6).cover?(n) && (0..1).cover?(route)
    pa=1-eta_a;pb=1-eta_b
    ca=pa*n;cb=pb*2*(6-n)
    route==1 ? pa*sigmoid(theta*(ca-cb)) : pb*sigmoid(theta*(cb-ca))
  end
  def counts(groups,held)
    result=Hash.new{|h,k|h[k]=[0,0]}
    groups.each do |(s,section,g,t),people|
      next if held.include?(s) || people.first['trt'].to_i!=3
      people.each do |r|
        raise 'Full info inconsistency' unless r['Informed'].to_i==1
        y=r['switchWill'].to_i
        raise 'invalid switch' unless y==0 || y==1
        key=[r['RouteA'].to_i,r['NumA'].to_i]
        a=result[key];a[0]+=y;a[1]+=1
      end
    end
    result
  end
  def loss(params,counts)
    counts.sum do |(route,n),(successes,total)|
      p=[[switch_probability(params,route,n),1e-12].max,1-1e-12].min
      -(successes*Math.log(p)+(total-successes)*Math.log(1-p))
    end
  end
  def fit(counts)
    raise ArgumentError,'empty training' if counts.empty?
    lower=[0.0001,0.0001,0.0001];upper=[0.9999,0.9999,5.0]
    seeds=[[0.6,0.45,0.4],[0.1,0.1,0.1],[0.9,0.9,0.8],[0.4,0.8,2.0]]
    best=nil
    seeds.each do |seed|
      x=seed.dup;fx=loss(x,counts);step=[0.14,0.14,0.2]
      500.times do
        improved=false
        3.times do |i|
          [-step[i],step[i]].each do |move|
            cand=x.dup;cand[i]=[[x[i]+move,lower[i]].max,upper[i]].min
            z=loss(cand,counts)
            if z<fx-1e-12
              x=cand;fx=z;improved=true
            end
          end
        end
        step.map!{|s|s/2} unless improved
        break if step.max<1e-8
      end
      best={params:x,loss:fx} if best.nil? || fx<best[:loss]
    end
    best
  end
  def run(path)
    raise 'original CSV SHA mismatch' unless Digest::SHA256.file(path).hexdigest==E::SHA
    groups=O.source(path)
    sessions=groups.keys.map(&:first).uniq.sort
    raise '24 sessions' unless sessions.size==24
    folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    data=[];fits=[]
    6.times do |f|
      held=sessions.select{|s|folds[s]==f}
      model=fit(counts(groups,held))
      fits<<{fold:f,**model}
      groups.each do |(s,section,g,t),people|
        next unless held.include?(s) && people.first['trt'].to_i==3
        probs=people.map{|r|switch_probability(model[:params],r['RouteA'].to_i,r['NumA'].to_i)}
        score=M.group_score(people,probs)
        data<<{epoch:E.epoch(t),score:score}
      end
    end
    raise '1872 groups required' unless data.size==1872
    by={all:data,early:data.select{|r|r[:epoch]==:early},
        middle:data.select{|r|r[:epoch]==:middle},
        late:data.select{|r|r[:epoch]==:late}}
    {sessions:24,groups:1872,parameters:fits,
     scores:by.to_h{|k,a|[k,{n:a.size,**[:joint,:count,:forecast_excess,:actual_excess].to_h{|z|
        [z,a.sum{|r|r[:score][z]}/a.size.to_f]}}]},
     scope:'Qi Part I Model A formula transferred to DIFFERENT full-information experiment; not original paper reproduction or out-of-source causal validation.'}
  end
end
puts JSON.pretty_generate(Rithm210QiModelATransfer.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
