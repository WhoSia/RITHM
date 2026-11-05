# frozen_string_literal: true
# P3-R16C: route-specific cost-gap logistic independent challenger for FULL information.
# Qi-inspired, not an exact Qi RDAB-SP reconstruction.
require_relative 'all_state_epoch_cv'
require 'digest'
require 'json'
module Rithm210FullInfoRouteGapLogit
  module_function
  M=Rithm210AllStateEpochCV
  E=Rithm210EpochIndependentWelfare
  O=Rithm210OnlineIdentity
  def sigmoid(z)
    return 1.0/(1.0+Math.exp(-z)) if z>=0
    v=Math.exp(z)
    v/(1.0+v)
  end
  def cost_gap(r)
    unless r['trt'].to_i==3 && r['Informed'].to_i==1
      raise ArgumentError,'requires full-information treatment'
    end
    n=r['NumA'].to_i
    raise ArgumentError,'current occupancy invalid' unless (0..6).cover?(n)
    ca=n.to_f;cb=2.0*(6-n)
    r['RouteA'].to_i==1 ? ca-cb : cb-ca
  end
  def fit_route(rows,ridge:0.01,maxiter:60)
    raise ArgumentError,'empty training or invalid ridge' if rows.empty? || ridge<0
    mean=(rows.sum{|x,y|y}+0.5)/(rows.length+1.0)
    intercept=Math.log(mean/(1-mean));slope=0.0
    maxiter.times do
      g0=-2*ridge*intercept;g1=-2*ridge*slope
      h00=2*ridge;h01=0.0;h11=2*ridge
      rows.each do |x,y|
        p=sigmoid(intercept+slope*x);w=p*(1-p)
        g0+=y-p;g1+=(y-p)*x
        h00+=w;h01+=w*x;h11+=w*x*x
      end
      det=h00*h11-h01*h01
      raise 'singular train Hessian' unless det>0
      d0=(h11*g0-h01*g1)/det
      d1=(h00*g1-h01*g0)/det
      d0=[[-2.0,d0].max,2.0].min
      d1=[[-2.0,d1].max,2.0].min
      intercept+=d0;slope+=d1
      break if d0.abs+d1.abs<1e-10
    end
    [intercept,slope]
  end
  def fit(groups,held)
    by_route={0=>[],1=>[]}
    groups.each do |(s,section,group,t),people|
      next if held.include?(s) || people.first['trt'].to_i!=3
      people.each do |r|
        route=r['RouteA'].to_i
        raise 'bad observed route' unless (0..1).cover?(route)
        y=r['switchWill'].to_i
        raise 'bad observed switch' unless (0..1).cover?(y)
        by_route[route]<<[cost_gap(r),y]
      end
    end
    by_route.transform_values{|rows|fit_route(rows)}
  end
  def probability(model,r)
    a,b=model.fetch(r['RouteA'].to_i)
    sigmoid(a+b*cost_gap(r))
  end
  def run(path)
    raise 'original CSV SHA mismatch' unless Digest::SHA256.file(path).hexdigest==E::SHA
    groups=O.source(path)
    sessions=groups.keys.map(&:first).uniq.sort
    raise '24 sessions' unless sessions.size==24
    folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    results=[];parameters=[]
    6.times do |f|
      held=sessions.select{|s|folds[s]==f}
      model=fit(groups,held)
      parameters<<{fold:f,route_a:model[1],route_b:model[0]}
      groups.each do |(s,section,g,t),people|
        next unless held.include?(s) && people.first['trt'].to_i==3
        p=people.map{|r|probability(model,r)}
        score=M.group_score(people,p)
        results<<{session:s,epoch:E.epoch(t),score:score}
      end
    end
    raise 'full-info group count mismatch' unless results.size==1872
    by={all:results,early:results.select{|r|r[:epoch]==:early},
        middle:results.select{|r|r[:epoch]==:middle},
        late:results.select{|r|r[:epoch]==:late}}
    {sessions:24,full_info_groups:1872,fold_parameters:parameters,
     summary:by.to_h{|k,a|[k,{n:a.size,**[:joint,:count,:forecast_excess,:actual_excess].to_h{|metric|
       [metric,a.sum{|r|r[:score][metric]}/a.size.to_f]}}]},
     limitations:'Same-source exploratory; route-specific cost-gap logistic NOT Qi RDAB-SP; conditional one-step score, not 40-period generative path.'}
  end
end
puts JSON.pretty_generate(Rithm210FullInfoRouteGapLogit.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
