# frozen_string_literal: true
# Nested decomposition of actual six-person congestion loss into
# within-stable-group temporal variation and between-group heterogeneity.
require_relative 'original_welfare_audit'
require 'json'
module Rithm210WelfareTemporalDecomposition
  module_function
  def components(groups,expected_groups:nil,expected_periods:nil)
    by_group=groups.group_by{|r|[r[:session],r[:group]]}
    raise 'wrong stable-group count' if expected_groups && by_group.size!=expected_groups
    means=[]
    within=[]
    by_group.each_value do |records|
      raise 'wrong period count' if expected_periods &&
        records.size!=expected_periods
      mu=records.sum{|r|r[:n]}/records.size.to_f
      means << mu
      within << records.sum{|r|(r[:n]-mu)**2}/records.size.to_f
    end
    raise 'unbalanced groups' unless by_group.values.map(&:size).uniq.size==1
    mu=means.sum/means.size
    var_between=means.sum{|m|(m-mu)**2}/means.size.to_f
    var_within=within.sum/within.size.to_f
    var_all=groups.sum{|r|(r[:n]-mu)**2}/groups.size.to_f
    raise 'variance identity failed' unless
      (var_all-var_within-var_between).abs<1e-9
    welfare=3*((mu-4)**2+var_all)
    actual=groups.sum{|r|3*(r[:n]-4)**2}/groups.size.to_f
    raise 'welfare identity failed' unless (welfare-actual).abs<1e-9
    {groups:by_group.size,periods_per_group:by_group.values.first.size,
      mean_a:mu,mean_bias_loss:3*(mu-4)**2,
      within_group_temporal_loss:3*var_within,
      between_group_mean_loss:3*var_between,total_excess:welfare}
  end
  def run(csv)
    source=Rithm210OriginalWelfareAudit.read_groups(csv)
    result=source.group_by{|r|[r[:treatment],r[:epoch]]}.map do |(t,ep),rs|
      periods=ep=='middle' ? 19 : 10
      {treatment:t,epoch:ep,**components(rs,
        expected_groups:48,expected_periods:periods)}
    end.sort_by{|r|[r[:treatment],r[:epoch]]}
    {n:source.size,group_periods:5616,results:result}
  end
end
puts JSON.pretty_generate(Rithm210WelfareTemporalDecomposition.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
