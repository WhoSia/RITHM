# frozen_string_literal: true
# Sharp real switching-cost bounds from only current and next occupancy.
# Hypothetical theta is a RESOURCE cost, not estimated psychological friction.
require_relative 'turnover_welfare_drift'
require 'json'

module Rithm210ChurnWelfareBounds
  module_function
  def turnover_bounds(n,m)
    raise ArgumentError,'occupancy' unless [n,m].all?{|x|
      x.is_a?(Integer) && x.between?(0,6)}
    delta=m-n
    d_min=[0,-delta].max
    d_max=[n,6-n-delta].min
    raise 'no feasible turnover' if d_min>d_max
    {minimum:delta.abs,maximum:2*d_max+delta,
      possible:(d_min..d_max).map{|d|2*d+delta}}
  end
  def exact_record(n:,u:,d:,theta:0)
    base=Rithm210TurnoverWelfareDrift.score(n,u,d)
    theta=Rational(theta)
    raise ArgumentError,'negative real switching cost' if theta<0
    m=n+base[:change]
    bounds=turnover_bounds(n,m)
    gross=u+d
    raise 'not in attainable bounds' unless bounds[:possible].include?(gross)
    {n:n,next_a:m,congestion:base[:subsequent],gross:gross,
      occupancy_identified_lower:base[:subsequent]+theta*bounds[:minimum],
      occupancy_identified_upper:base[:subsequent]+theta*bounds[:maximum],
      observed_turnover_welfare:base[:subsequent]+theta*gross,
      hidden_cancellation_churn:gross-bounds[:minimum]}
  end
  def report(csv)
    rows=Rithm210TurnoverWelfareDrift.records(csv)
    groups=rows.group_by{|r|[r[:treatment],r[:epoch]]}
    {n:rows.size,source:'sealed original six-person switching data',
      treatment_epoch:groups.to_h do |(t,epoch),records|
        costs=records.map{|r|exact_record(n:r[:n],u:r[:u],d:r[:d],theta:1)}
        count=records.size.to_f
        ["#{t}_#{epoch}",{
          n:records.size,
          mean_gross_switches:costs.sum{|r|r[:gross]}/count,
          mean_min_from_occupancy:records.sum{|r|r[:change].abs}/count,
          mean_extra_cancelled_switches:costs.sum{|r|r[:hidden_cancellation_churn]}/count,
          mean_occupancy_only_max:records.sum{|r|
            turnover_bounds(r[:n],r[:n]+r[:change])[:maximum]}/count,
          mean_next_congestion_excess:costs.sum{|r|r[:congestion]}/count,
          mean_total_excess_if_theta_one:costs.sum{|r|r[:observed_turnover_welfare]}/count}]
      end}
  end
end
puts JSON.pretty_generate(Rithm210ChurnWelfareBounds.report(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
