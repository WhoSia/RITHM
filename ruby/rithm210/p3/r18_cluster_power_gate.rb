# frozen_string_literal: true
# R18P0 2x2 four-arm cluster-level interaction planning from historical session
# 40-period welfare variation. Not a registered trial or validated treatment variance.
require 'csv'
require 'digest'
require 'json'
module Rithm210R18ClusterPowerGate
  module_function
  SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'
  Z_ALPHA=1.959963984540054
  Z_POWER=0.8416212335729143
  def cost(n)
    raise ArgumentError,'occupancy' unless n.is_a?(Integer) && n.between?(0,6)
    n*n+2*(6-n)**2
  end
  def source_paths(path)
    raise 'original CSV SHA mismatch' unless Digest::SHA256.file(path).hexdigest==SHA
    groups=Hash.new{|h,k|h[k]=[]}
    CSV.foreach(path,headers:true) do |r|
      s=r['session'].to_i;t=r['Period'].to_i;trt=r['trt'].to_i
      next unless trt==3 && s!=2 && s!=101 && t.between?(1,39)
      groups[[s,r['section'].to_i,r['Group'].to_i,t]]<<r
    end
    raise '1872 six-person groups required' unless groups.size==1872 && groups.values.all?{|v|v.size==6}
    by=Hash.new{|h,k|h[k]=[]}
    groups.each do |(s,section,g,t),rows|
      by[[s,section,g]]<<[t,rows.first['NumA'].to_i,rows.first['NumAnext'].to_i]
    end
    paths=by.map do |(s,section,g),rows|
      rows.sort_by!(&:first)
      raise '39 consecutive periods' unless rows.map(&:first)==(1..39).to_a
      rows.each_cons(2){|a,b|raise 'broken occupancy continuity' unless a[2]==b[1]}
      ns=rows.map{|r|r[1]}+[rows.last[2]]
      {session:s,total:ns.sum{|n|cost(n)}}
    end
    raise '48 complete paths required' unless paths.size==48
    paths
  end
  def sample_sd(values)
    raise ArgumentError,'need at least two observations' unless values.size>=2
    avg=values.sum.to_f/values.size
    Math.sqrt(values.sum{|x|(x-avg)**2}/(values.size-1).to_f)
  end
  def summarize(paths)
    by=paths.group_by{|r|r.fetch(:session)}
    raise '24 sessions and 48 group paths required' unless by.size==24 && by.values.sum(&:size)==48 && by.values.all?{|v|!v.empty?}
    sessions=by.values.map{|v|v.sum{|r|r[:total]}/v.size.to_f}
    totals=paths.map{|r|r[:total]}
    {sessions:by.size,group_paths:paths.size,mean_group_total:totals.sum.to_f/totals.size,
     group_sd:sample_sd(totals),session_mean_sd:sample_sd(sessions),
     group_paths_per_session:by.values.map(&:size).tally,
     min_session_mean:sessions.min,max_session_mean:sessions.max}
  end
  def clusters_per_arm(sd:,target:)
    raise ArgumentError,'finite positive SD and effect' unless sd.is_a?(Numeric) && sd.finite? && sd>0 && target.is_a?(Numeric) && target.finite? && target>0
    [(4*(Z_ALPHA+Z_POWER)**2*(sd/target)**2).ceil,2].max
  end
  def minimum_detectable(sd:,clusters_per_arm:)
    raise ArgumentError,'clusters per arm at least two' unless clusters_per_arm.is_a?(Integer) && clusters_per_arm>=2
    2*(Z_ALPHA+Z_POWER)*sd/Math.sqrt(clusters_per_arm)
  end
  def run(path)
    historical=summarize(source_paths(path))
    sd=historical[:session_mean_sd]
    {historical:historical,design:'4-arm balanced independent-session ITT interaction, two-sided alpha .05, nominal power .8, equal variance and normal approximation',
     target_cost_effects:[10,20,30,40,50,70].map{|d|{target:d,clusters_per_arm:clusters_per_arm(sd:sd,target:d),all_clusters:4*clusters_per_arm(sd:sd,target:d)}},
     mde_if_six_clusters_per_arm:minimum_detectable(sd:sd,clusters_per_arm:6),
     warning:'Only a rough hypothetical planning calculation. Historical Full-information session-mean variance may change with randomized disclosure and time schedule. No participant recruitment, intervention, or verified actual power.'}
  end
end
puts JSON.pretty_generate(Rithm210R18ClusterPowerGate.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
