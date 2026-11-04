# frozen_string_literal: true
# Appendix B SSM5 decision rule evaluated CONDITIONALLY on recorded real histories.
# NOT the authors' free-running 40-period simulation or a Table 7 replication.
require_relative 'activity_event_cv'
require 'json'
module Rithm210SSM5Conditioned
  module_function
  def choose_a(history,informed:,rng:,draws:128,q:5)
    raise ArgumentError,'draws positive' unless draws.positive? && q.positive?
    return 0.5 if history[:delta].empty?
    a=history[:a];b=history[:b];delta=history[:delta]
    return 0.5 unless informed || (!a.empty? && !b.empty?)
    sum=0.0
    draws.times do
      if informed
        advantage=q.times.sum{delta.fetch(rng.rand(delta.length))}
      else
        advantage=q.times.sum{a.fetch(rng.rand(a.length))}-
          q.times.sum{b.fetch(rng.rand(b.length))}
      end
      sum += advantage>0 ? 1.0 : advantage==0 ? 0.5 : 0.0
    end
    sum/draws
  end
  def make_history
    {delta:[],a:[],b:[]}
  end
  def add_trial(history,row)
    n=row['NumA'].to_i
    choice_a=row['RouteA'].to_i==1
    others=n-(choice_a ? 1 : 0)
    cost_a=others+1
    cost_b=2*(6-others)
    # Other-route payoffs only accessible to the informed agent.
    # Uninformed agent samples realized profits conditional on chosen action.
    history[:delta] << (cost_b-cost_a)
    history[choice_a ? :a : :b] << row['profit'].to_f
  end
  def run(csv,draws:128,seed:20261104)
    groups=Rithm210OnlineIdentity.source(csv)
    raise 'source SHA mismatch' unless Digest::SHA256.file(csv).hexdigest==Rithm210ActivityEventCV::SHA
    rows=[]
    history=Hash.new{|h,k|h[k]=make_history}
    rng=Random.new(seed)
    keys=groups.keys.sort_by{|s,sec,g,t|[s,sec,t,g]}
    keys.each do |s,section,g,t|
      actors=groups.fetch([s,section,g,t])
      # Current observed trial t is complete. It can inform choice at t+1,
      # but future t+1 actions/costs must not be used in its prediction.
      actors.each do |r|
        add_trial(history[[s,section,r['ID'].to_i]],r)
      end
      prob=actors.map do |r|
        h=history[[s,section,r['ID'].to_i]]
        choose_a(h,informed:r['Informed'].to_i==1,rng:rng,draws:draws)
      end
      switch_prob=actors.each_with_index.map{|r,i|r['RouteA'].to_i==1 ? 1.0-prob[i] : prob[i]}
      predicted=Rithm210ActivityEventCV.event_probabilities(actors,switch_prob)
      u=actors.sum{|r|r['switchBtoAWill'].to_i}
      d=actors.sum{|r|r['switchAtoBWill'].to_i}
      observed_loss=3*(actors.first['NumAnext'].to_i-4)**2
      evt1=u+d==0 ? 1 : 0
      evt2=u==d && u>0 ? 1 : 0
      rows << {session:s,period:t,treatment:actors.first['trt'].to_i,n:actors.first['NumA'].to_i,
        no_switch_brier:(predicted[:none]-evt1)**2,
        cancel_brier:(predicted[:cancel]-evt2)**2,
        welfare_mse:(predicted[:next_loss]-observed_loss)**2,
        no_switch_pred:predicted[:none],no_switch_obs:evt1,
        cancel_pred:predicted[:cancel],cancel_obs:evt2}
    end
    raise 'coverage' unless rows.size==5616
    summarize=->(a){ {n:a.size}.merge([:no_switch_brier,:cancel_brier,:welfare_mse,
      :no_switch_pred,:no_switch_obs,:cancel_pred,:cancel_obs].to_h{|k|[k,a.sum{|r|r[k]}/a.size.to_f]})}
    {draws:draws,seed:seed,scope:'conditioned one-step SSM5, NOT original free-running simulation',
      overall:summarize.call(rows),
      full_n4_early:summarize.call(rows.select{|r|r[:treatment]==3 && r[:n]==4 && r[:period]<=10}),
      full_n4_late:summarize.call(rows.select{|r|r[:treatment]==3 && r[:n]==4 && r[:period]>=30})}
  end
end
puts JSON.pretty_generate(Rithm210SSM5Conditioned.run(ARGV.fetch(0),
  draws:Integer(ARGV.fetch(1,'128')),seed:Integer(ARGV.fetch(2,'20261104')))) if __FILE__==$PROGRAM_NAME
