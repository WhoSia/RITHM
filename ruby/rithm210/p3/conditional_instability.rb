# frozen_string_literal: true
require_relative 'turnover_welfare_drift'
require 'json'

module Rithm210ConditionalInstability
  module_function
  def aggregate(rows)
    raise 'empty conditional cell' if rows.empty?
    n=rows.size.to_f
    {n:rows.size,expected_next_loss:rows.sum{|r|r[:subsequent]}/n,
      net_move_zero:rows.count{|r|r[:change]==0}/n,
      gross_switch_zero:rows.count{|r|r[:u]+r[:d]==0}/n,
      cancellation:rows.count{|r|r[:u]>0 && r[:d]>0 && r[:change]==0}/n,
      mean_squared_change:rows.sum{|r|r[:change]**2}/n}
  end
  def conditional_by_epoch(rows,trt:,n:)
    %i[early late].to_h do |ep|
      subset=rows.select{|r|r[:treatment]==trt && r[:epoch]==ep && r[:n]==n}
      [ep,aggregate(subset)]
    end
  end
  def paired_bootstrap(rows,trt:3,n:4,draws:20_000,seed:20261104)
    groups=rows.select{|r|r[:treatment]==trt && r[:n]==n &&
      [:early,:late].include?(r[:epoch])}.group_by{|r|r[:session]}
    raise 'wrong session panel' unless groups.size==24
    counts=groups.keys.sort.map do |s|
      [:early,:late].map do |ep|
        a=groups.fetch(s).select{|r|r[:epoch]==ep}
        # A session may contain zero occurrences of current n in an epoch.
        # Preserve its zero-count cell; resample whole sessions and pool by n.
        [a.length,a.sum{|r|r[:subsequent]},a.count{|r|r[:change]==0},
          a.count{|r|r[:u]+r[:d]==0},
          a.count{|r|r[:u]>0 && r[:d]>0 && r[:change]==0}]
      end
    end
    contrast=->(sample,index){
      en=sample.sum{|a|a[0][0]};ln=sample.sum{|a|a[1][0]}
      raise 'bootstrap no support' unless en>0 && ln>0
      sample.sum{|a|a[0][index]}/en.to_f -
        sample.sum{|a|a[1][index]}/ln.to_f
    }
    rng=Random.new(seed)
    {next_loss_decline:1,net_zero_early_minus_late:2,
      gross_zero_early_minus_late:3,
      cancellation_early_minus_late:4}.to_h do |name,index|
      values=Array.new(draws) do
        contrast.call(Array.new(counts.size){counts.fetch(rng.rand(counts.size))},index)
      end.sort
      [name,{point:contrast.call(counts,index),
        lower:values[(draws*0.025).floor],upper:values[(draws*0.975).floor]}]
    end
  end
  def report(csv,draws:20_000)
    rows=Rithm210TurnoverWelfareDrift.records(csv)
    {full_optimal_current_state:conditional_by_epoch(rows,trt:3,n:4),
      full_optimal_state_contrast:paired_bootstrap(rows,draws:draws),
      no_optimal_current_state:conditional_by_epoch(rows,trt:1,n:4)}
  end
end
puts JSON.pretty_generate(Rithm210ConditionalInstability.report(ARGV.fetch(0),
  draws:Integer(ARGV.fetch(1,'20000')))) if $PROGRAM_NAME==__FILE__
