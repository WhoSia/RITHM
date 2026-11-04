# frozen_string_literal: true
# P3-R7: cluster uncertainty in observed SSM optimal-state activity gap.
require_relative 'turnover_welfare_drift'
require 'json'
module Rithm210SSMObservedActivityGap
  module_function
  def blocks(csv)
    rows=Rithm210TurnoverWelfareDrift.records(csv)
    sessions=rows.map{|r|r[:session]}.uniq.sort
    raise '24 sessions required' unless sessions.size==24
    out=sessions.to_h{|s|[s,{early:[0,0],late:[0,0]}]}
    rows.each do |r|
      next unless r[:treatment]==3 && r[:n]==4 &&
        [:early,:late].include?(r[:epoch])
      cell=out.fetch(r[:session]).fetch(r[:epoch])
      cell[0]+=1
      cell[1]+=1 if r[:u]==0 && r[:d]==0
    end
    out
  end
  def rates(by_session,selected)
    [:early,:late].to_h do |epoch|
      n=selected.sum{|s|by_session.fetch(s).fetch(epoch)[0]}
      count=selected.sum{|s|by_session.fetch(s).fetch(epoch)[1]}
      raise 'no support' unless n>0
      [epoch,{n:n,count:count,rate:count.to_f/n}]
    end
  end
  def compare(by_session,sim_early:,sim_late:,draws:20_000,seed:20261104)
    sessions=by_session.keys.sort
    observed=rates(by_session,sessions)
    sim_change=sim_late-sim_early
    actual_change=observed[:late][:rate]-observed[:early][:rate]
    rng=Random.new(seed)
    samples=Array.new(draws) do
      chosen=Array.new(sessions.size){sessions.fetch(rng.rand(sessions.size))}
      p=rates(by_session,chosen)
      p[:late][:rate]-p[:early][:rate]-sim_change
    end.sort
    {observed:observed,observed_change:actual_change,
      simulated_change:sim_change,gap:actual_change-sim_change,
      percentile95:[samples[(draws*0.025).floor],samples[(draws*0.975).floor]],
      scope:'observed session uncertainty only; simulation MC uncertainty excluded'}
  end
end
if __FILE__==$PROGRAM_NAME
  sim=JSON.parse(File.read(ARGV.fetch(1)))['results']['ssm5_3']
  puts JSON.pretty_generate(Rithm210SSMObservedActivityGap.compare(
    Rithm210SSMObservedActivityGap.blocks(ARGV.fetch(0)),
    sim_early:sim['early']['no_switch_rate'],
    sim_late:sim['late']['no_switch_rate']))
end
