# frozen_string_literal: true
# Common-state support comparison: current group A occupancy n=3,4,5.
# Uniform weights are fixed, not chosen from outcome magnitudes.
require_relative 'turnover_welfare_drift'
require 'json'

module Rithm210StateStandardizedInstability
  module_function
  STATES=[3,4,5].freeze
  def cell_data(rows)
    out=Hash.new{|h,k|h[k]=[0,0]}
    rows.each do |r|
      next unless STATES.include?(r[:n]) && [:early,:late].include?(r[:epoch])
      key=[r[:session],r[:treatment],r[:epoch],r[:n]]
      out[key][0]+=1
      out[key][1]+=r[:subsequent]
    end
    out
  end
  def standardized(data,sessions,treatment,epoch)
    STATES.sum do |n|
      count=0
      sum=0
      sessions.each do |s|
        a=data.fetch([s,treatment,epoch,n],[0,0])
        count+=a[0]
        sum+=a[1]
      end
      raise 'missing common state support' if count==0
      sum.to_f/count/STATES.size
    end
  end
  def changes(data,sessions)
    by_treatment=(1..3).to_h do |treatment|
      early=standardized(data,sessions,treatment,:early)
      late=standardized(data,sessions,treatment,:late)
      [treatment,{early:early,late:late,decline:early-late}]
    end
    {treatments:by_treatment,
      full_minus_no_decline:by_treatment[3][:decline]-by_treatment[1][:decline]}
  end
  def report(csv,draws:20_000,seed:20261104)
    groups=Rithm210TurnoverWelfareDrift.records(csv)
    data=cell_data(groups)
    sessions=groups.map{|r|r[:session]}.uniq.sort
    raise 'session count' unless sessions.size==24
    observed=changes(data,sessions)
    rng=Random.new(seed)
    metrics={}
    (1..3).each{|t|metrics["t#{t}_decline".to_sym]=->(x){x[:treatments][t][:decline]}}
    metrics[:full_minus_no_decline]=->(x){x[:full_minus_no_decline]}
    samples=metrics.to_h{|key,_|[key,[]]}
    draws.times do
      selected=Array.new(sessions.size){sessions.fetch(rng.rand(sessions.size))}
      value=changes(data,selected)
      metrics.each{|key,fn|samples[key]<<fn.call(value)}
    end
    intervals=metrics.to_h do |key,fn|
      a=samples[key].sort
      [key,{point:fn.call(observed),lower:a[(draws*0.025).floor],
        upper:a[(draws*0.975).floor]}]
    end
    {states:STATES,reference:'uniform over current A occupancy 3,4,5',
      n:groups.size,observed:observed,session_bootstrap:intervals}
  end
end
puts JSON.pretty_generate(Rithm210StateStandardizedInstability.report(ARGV.fetch(0),
  draws:Integer(ARGV.fetch(1,'20000')))) if $PROGRAM_NAME==__FILE__
