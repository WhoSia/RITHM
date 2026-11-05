# frozen_string_literal: true
# P3-R16E: Qi et al. (2023) Part I §5.1 Models B/C, plus A as existing.
# Identical Full-info 24-session fold transfer; not original Qi experiment.
require_relative 'qi_model_a_transfer'
require_relative 'epoch_independent_welfare'
require 'digest'
require 'json'
module Rithm210QiABCTest
  module_function
  Q=Rithm210QiModelATransfer
  E=Rithm210EpochIndependentWelfare
  O=Rithm210OnlineIdentity
  M=Rithm210AllStateEpochCV
  VARIANTS=[:a,:b,:c].freeze
  def probability(kind,params,route,n)
    raise ArgumentError,'unknown Qi variant' unless VARIANTS.include?(kind)
    return Q.switch_probability(params,route,n) if kind==:a
    raise ArgumentError,'invalid occupancy/route' unless (0..6).cover?(n) && (0..1).cover?(route)
    theta=params[-1]
    etas=kind==:b ? [params[0],params[0]] : params[0,2]
    raise ArgumentError,'invalid constrained Qi parameters' unless theta.positive? && etas.all?{|v|v.between?(0,1)}
    reconsider=1-etas[route==1 ? 0 : 1]
    cost_gap=route==1 ? 3*n-12 : 12-3*n
    reconsider*Q.sigmoid(theta*cost_gap)
  end
  def neglog(kind,params,cells)
    cells.sum do |(route,n),(successes,total)|
      p=[[probability(kind,params,route,n),1e-12].max,1-1e-12].min
      -successes*Math.log(p)-(total-successes)*Math.log(1-p)
    end
  end
  def fit(kind,cells)
    raise ArgumentError,'empty train cells' if cells.empty?
    return Q.fit(cells) if kind==:a
    seeds=kind==:b ? [[0.5,0.2],[0.9,0.7],[0.2,1.5]] : [[0.5,0.5,0.2],[0.8,0.2,0.7],[0.2,0.8,1.5]]
    lower=Array.new(seeds.first.size,0.0001)
    upper=Array.new(seeds.first.size,0.9999);upper[-1]=5.0
    best=nil
    seeds.each do |initial|
      x=initial.dup
      val=neglog(kind,x,cells)
      steps=Array.new(x.size,0.2)
      550.times do
        improved=false
        x.length.times do |i|
          [-steps[i],steps[i]].each do |delta|
            y=x.dup;y[i]=[[x[i]+delta,lower[i]].max,upper[i]].min
            v=neglog(kind,y,cells)
            if v < val-1e-11
              x=y;val=v;improved=true
            end
          end
        end
        steps.map!{|s|s*0.5} unless improved
        break if steps.max<1e-8
      end
      best={params:x,loss:val} if best.nil? || val<best[:loss]
    end
    best
  end
  def run(path)
    raise 'original SHA mismatch' unless Digest::SHA256.file(path).hexdigest==E::SHA
    groups=O.source(path)
    sessions=groups.keys.map(&:first).uniq.sort
    raise '24 sessions required' unless sessions.size==24
    fold=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    fitted=[]
    scores=Hash.new{|h,k|h[k]=[]}
    6.times do |f|
      held=sessions.select{|s|fold[s]==f}
      cells=Q.counts(groups,held)
      params=VARIANTS.to_h{|kind|[kind,fit(kind,cells)]}
      fitted<<{fold:f,**params}
      groups.each do |(s,sec,g,t),people|
        next unless held.include?(s) && people.first['trt'].to_i==3
        VARIANTS.each do |kind|
          ps=people.map{|r|probability(kind,params.fetch(kind)[:params],r['RouteA'].to_i,r['NumA'].to_i)}
          scores[[kind,E.epoch(t)]]<<M.group_score(people,ps)
        end
      end
    end
    coverage=scores.values.sum(&:size)
    raise '3 models x 1872 groups required' unless coverage==5616
    by=scores.to_h{|key,rs|[key.join('_'),{n:rs.size,**[:joint,:count,:forecast_excess,:actual_excess].to_h{|metric|
      [metric,rs.sum{|r|r[metric]}/rs.size.to_f]}}]}
    all=VARIANTS.to_h do |kind|
      a=scores.select{|(m,e),v|m==kind}.values.flatten
      [kind,{n:a.size,**[:joint,:count,:forecast_excess,:actual_excess].to_h{|metric|
        [metric,a.sum{|r|r[metric]}/a.size.to_f]}}]
    end
    {sessions:24,full_groups:1872,model_count:3,fitted:fitted,by_epoch:by,overall:all,
     limitation:'Independent human dataset transfer of Qi Part I A/B/C forms, within-source exploratory out-of-session folds; no causal/external confirmation.'}
  end
end
puts JSON.pretty_generate(Rithm210QiABCTest.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
