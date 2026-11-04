# frozen_string_literal: true
# Bootstrap exact original group congestion cost decomposition by full sessions.
require_relative 'original_welfare_audit'
require 'json'
module Rithm210WelfareDecomposition
  module_function
  def sufficient_statistics(groups)
    out=Hash.new{|h,k|h[k]=[0,0,0]}
    groups.each do |g|
      next unless %w[early late].include?(g[:epoch])
      a=out[[g[:session],g[:treatment],g[:epoch]]]
      a[0]+=1; a[1]+=g[:n]; a[2]+=g[:n]**2
    end
    out
  end
  def components(stats,sessions,treatment,epoch)
    n=sum=sum_sq=0
    sessions.each do |s|
      a=stats.fetch([s,treatment,epoch])
      n+=a[0];sum+=a[1];sum_sq+=a[2]
    end
    mu=sum.to_f/n
    variance=sum_sq.to_f/n-mu*mu
    {bias:3*(mu-4)**2,dispersion:3*variance,
      total:3*(sum_sq.to_f/n-8*mu+16)}
  end
  def differences(stats,sessions)
    fe=components(stats,sessions,3,'early')
    fl=components(stats,sessions,3,'late')
    ne=components(stats,sessions,1,'early')
    nl=components(stats,sessions,1,'late')
    {full_bias_decline:fe[:bias]-fl[:bias],
      full_dispersion_decline:fe[:dispersion]-fl[:dispersion],
      full_total_decline:fe[:total]-fl[:total],
      no_total_decline:ne[:total]-nl[:total],
      full_vs_no_total_decline:(fe[:total]-fl[:total])-(ne[:total]-nl[:total])}
  end
  def run(csv,draws:20_000,seed:20261104)
    stats=sufficient_statistics(Rithm210OriginalWelfareAudit.read_groups(csv))
    sessions=stats.keys.map(&:first).uniq.sort
    raise '24 session mismatch' unless sessions.size==24
    point=differences(stats,sessions)
    rng=Random.new(seed)
    boot=Hash.new{|h,k|h[k]=[]}
    draws.times do
      chosen=Array.new(sessions.size){sessions.fetch(rng.rand(sessions.size))}
      differences(stats,chosen).each{|metric,val|boot[metric]<<val}
    end
    {sessions:24,draws:draws,estimates:point.to_h do |metric,value|
      values=boot[metric].sort
      [metric,{point:value,lower:values[(draws*0.025).floor],
        upper:values[(draws*0.975).floor]}]
    end}
  end
end
if __FILE__==$PROGRAM_NAME
  puts JSON.pretty_generate(Rithm210WelfareDecomposition.run(ARGV.fetch(0)))
end
