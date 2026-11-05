# frozen_string_literal: true
# P3-R16F: genuine unconditional 40-period occupancy forecasting from initial n only.
# Contrasts repeated observed-state 1-step scores with autonomous group Markov rollouts.
require_relative 'qi_abc_transfer'
require_relative 'finite_horizon_independent_welfare'
require 'digest'
require 'json'
module Rithm210QiABCForwardTrajectory
  module_function
  Q=Rithm210QiABCTest
  O=Rithm210OnlineIdentity
  E=Rithm210EpochIndependentWelfare
  M=Rithm210AllStateEpochCV
  F=Rithm210FiniteHorizonIndependentWelfare
  VARIANTS=[:markov,:epoch20,:a,:b,:c].freeze
  def actor_state(route,n)
    raise ArgumentError,'route/n' unless (0..1).cover?(route) && (0..6).cover?(n)
    {'trt'=>'3','Informed'=>'1','RouteA'=>route.to_s,
     'Cost'=>(route==1 ? n : 2*(6-n)).to_s}
  end
  def probabilities(variant,fit,n,period)
    raise ArgumentError,'unsupported variant' unless VARIANTS.include?(variant)
    return [Q.probability(variant,fit.fetch(variant),1,n),
            Q.probability(variant,fit.fetch(variant),0,n)] if Q::VARIANTS.include?(variant)
    basefit=fit.fetch(:markov)
    pa=O.probability(basefit,actor_state(1,n))
    pb=O.probability(basefit,actor_state(0,n))
    return [pa,pb] if variant==:markov
    tally=fit.fetch(:epoch_counts)
    [E.probability(pa,tally,actor_state(1,n),period),
     E.probability(pb,tally,actor_state(0,n),period)]
  end
  def kernel(variant,fit,period)
    (0..6).map do |n|
      down,up=probabilities(variant,fit,n,period)
      pd=M.convolve(Array.new(n,down))
      pu=M.convolve(Array.new(6-n,up))
      row=Array.new(7,0.0)
      pu.each_with_index{|v,u|pd.each_with_index{|w,d|row[n+u-d]+=v*w}}
      raise 'not stochastic' unless (row.sum-1).abs<1e-10
      row
    end
  end
  def propagate(dist,kernel)
    raise ArgumentError,'7 states required' unless dist.size==7
    (0..6).map{|j|(0..6).sum{|i|dist[i]*kernel[i][j]}}
  end
  def forecast(variant,fit,initial:,horizon:40)
    raise ArgumentError,'invalid initial or horizon' unless (0..6).cover?(initial) && horizon.is_a?(Integer) && horizon.positive?
    dist=Array.new(7,0.0);dist[initial]=1.0
    total=0.0
    horizon.times do |i|
      total+=(0..6).sum{|n|dist[n]*F.cost(n)}
      dist=propagate(dist,kernel(variant,fit,i+1)) if i+1<horizon
    end
    raise 'forecast probability mass lost' unless (dist.sum-1).abs<1e-9
    {expected_total_cost:total,terminal:dist}
  end
  def extract_trajectories(groups,held)
    by=Hash.new{|h,k|h[k]=[]}
    groups.each do |(s,section,g,t),people|
      next unless held.include?(s) && people.first['trt'].to_i==3
      by[[s,section,g]]<<[t,people.first['NumA'].to_i,people.first['NumAnext'].to_i]
    end
    by.map do |(s,section,g),rows|
      rows.sort_by!(&:first)
      raise '39 consecutive periods required' unless rows.map(&:first)==(1..39).to_a
      rows.each_cons(2){|x,y|raise 'broken next-occupancy continuity' unless x[2]==y[1]}
      a=rows.map{|t,n,nn|n}+[rows.last[2]]
      raise '40 occupancies required' unless a.size==40 && a.all?{|n|(0..6).cover?(n)}
      {session:s,section:section,group:g,initial:a.first,terminal:a.last,
       observed_total_cost:a.sum{|n|F.cost(n)}}
    end
  end
  def run(csv)
    raise 'original CSV SHA mismatch' unless Digest::SHA256.file(csv).hexdigest==E::SHA
    groups=O.source(csv)
    sessions=groups.keys.map(&:first).uniq.sort
    raise '24 original sessions required' unless sessions.size==24
    fold=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    metrics=Hash.new{|h,k|h[k]=[]}
    6.times do |f|
      held=sessions.select{|s|fold[s]==f}
      cells=Rithm210QiModelATransfer.counts(groups,held)
      fitted=Q::VARIANTS.to_h{|v|[v,Q.fit(v,cells)[:params]]}
      fitted[:markov]=O.train(groups,held)
      fitted[:epoch_counts]=E.train_epoch(groups,held)
      extract_trajectories(groups,held).each do |trajectory|
        VARIANTS.each do |variant|
          pred=forecast(variant,fitted,initial:trajectory[:initial],horizon:40)
          truth=trajectory[:observed_total_cost]
          error=pred[:expected_total_cost]-truth
          mass=[pred[:terminal].fetch(trajectory[:terminal]),1e-300].max
          metrics[variant]<<{session:trajectory[:session],error:error,absolute_error:error.abs,
            squared_error:error**2,terminal_logloss:-Math.log(mass),
            expected_total:pred[:expected_total_cost],observed_total:truth}
        end
      end
    end
    raise '48 trajectories per five models expected' unless metrics.values.all?{|rows|rows.size==48}
    {sessions:24,complete_40period_trajectories:48,
     model_summary:metrics.to_h{|variant,rows|[variant,[:error,:absolute_error,:squared_error,
       :terminal_logloss,:expected_total,:observed_total].to_h{|metric|
       [metric,rows.sum{|r|r[metric]}/rows.size.to_f]}]},
     limitations:'Unconditional from initial n1; 39 autonomous Markov transitions; epoch20 uses calendar period only; 48 observed paths; same source repeatedly explored, no causal intervention or new-study external test.'}
  end
end
puts JSON.pretty_generate(Rithm210QiABCForwardTrajectory.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
