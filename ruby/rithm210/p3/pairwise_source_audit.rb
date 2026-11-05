# frozen_string_literal: true
# Sealed-source 24-session group bootstrap for exact pairwise congestion-welfare terms.
require_relative 'turnover_welfare_drift'
require_relative 'pairwise_welfare'
require 'json'
module Rithm210PairwiseSourceAudit
  module_function
  KEYS=[:gross,:same_direction_pairs,:opposing_pairs,:pair_balance,:next_loss].freeze
  def group_records(csv)
    raw=Rithm210TurnoverWelfareDrift.records(csv)
    sessions=raw.map{|r|r[:session]}.uniq.sort
    raise '24 sessions expected' unless sessions.size==24
    rows=raw.filter_map do |r|
      next unless r[:treatment]==3 && r[:n]==4 && [:early,:late].include?(r[:epoch])
      {session:r[:session],epoch:r[:epoch],
        **Rithm210PairwiseWelfare.decompose(up:r[:up],down:r[:down],current_a:r[:n])}
    end
    raise 'source n4 support changed' unless rows.group_by{|r|r[:epoch]}.transform_values(&:size)=={early:154,late:257}
    [sessions,rows]
  end
  def session_totals(sessions,rows)
    out=sessions.to_h{|s|[s,{early:Hash.new(0),late:Hash.new(0)}]}
    rows.each do |r|
      a=out.fetch(r[:session]).fetch(r[:epoch])
      a[:n]+=1
      KEYS.each{|k|a[k]+=r.fetch(k)}
      a[:no_switch]+=1 if r[:gross]==0
    end
    out
  end
  def summary(totals,selected)
    [:early,:late].to_h do |epoch|
      count=selected.sum{|s|totals.fetch(s).fetch(epoch)[:n]}
      raise 'zero support after session resampling' unless count>0
      [epoch,{n:count}.merge((KEYS+[:no_switch]).to_h do |k|
        sum=selected.sum{|s|totals.fetch(s).fetch(epoch)[k]}
        [k,sum.to_f/count]
      end)]
    end
  end
  def contrasts(stats)
    a=stats.fetch(:early);b=stats.fetch(:late)
    gross=3*(a[:gross]-b[:gross])
    pair=6*(a[:pair_balance]-b[:pair_balance])
    welfare=a[:next_loss]-b[:next_loss]
    raise 'decomposition not exact' unless (gross+pair-welfare).abs<1e-9
    {cost_decline:welfare,gross_component:gross,pair_component:pair,
      gross_decline:a[:gross]-b[:gross],
      cancellation_pair_decline:a[:opposing_pairs]-b[:opposing_pairs]}
  end
  def evaluate(csv,draws:20_000,seed:20261105)
    sessions,rows=group_records(csv)
    totals=session_totals(sessions,rows)
    point=summary(totals,sessions)
    differences=contrasts(point)
    rng=Random.new(seed)
    boots=differences.to_h{|k,_|[k,[]]}
    draws.times do
      sampled=Array.new(sessions.size){sessions.fetch(rng.rand(sessions.size))}
      contrasts(summary(totals,sampled)).each{|k,v|boots.fetch(k)<<v}
    end
    cis=boots.to_h do |k,vals|
      x=vals.sort
      [k,{point:differences[k],lower:x[(draws*0.025).floor],
        upper:x[(draws*0.975).floor]}]
    end
    {source_groups:5616,full_current_n4:point,bootstrap_sessions:24,
      bootstrap_draws:draws,contrasts:cis}
  end
end
if __FILE__==$PROGRAM_NAME
  puts JSON.pretty_generate(Rithm210PairwiseSourceAudit.evaluate(ARGV.fetch(0),
    draws:Integer(ARGV.fetch(1,'20000'))))
end
