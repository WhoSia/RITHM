# frozen_string_literal: true
# Whole-session bootstrap of gross and occupancy-invisible cancelling switches.
require_relative 'churn_welfare_bounds'
require 'json'
module Rithm210ChurnSessionBootstrap
  module_function
  def summaries(rows)
    counts=Hash.new{|h,k|h[k]=[0,0,0]}
    rows.each do |r|
      next unless [:early,:late].include?(r[:epoch])
      c=counts[[r[:session],r[:treatment],r[:epoch]]]
      c[0]+=1
      c[1]+=r[:u]+r[:d]
      c[2]+=r[:u]+r[:d]-r[:change].abs
    end
    counts
  end
  def mean(counts,sessions,t,e,index)
    denominator=numerator=0
    sessions.each do |s|
      a=counts.fetch([s,t,e])
      denominator+=a[0]
      numerator+=a[index]
    end
    raise 'no observations' if denominator==0
    numerator.to_f/denominator
  end
  def contrast(counts,sessions,index)
    full=mean(counts,sessions,3,:early,index)-mean(counts,sessions,3,:late,index)
    no=mean(counts,sessions,1,:early,index)-mean(counts,sessions,1,:late,index)
    {full_decline:full,no_decline:no,full_minus_no:full-no}
  end
  def run(csv,draws:20_000,seed:20261104)
    records=Rithm210TurnoverWelfareDrift.records(csv)
    counts=summaries(records)
    sessions=records.map{|r|r[:session]}.uniq.sort
    raise 'must have 24 sessions' unless sessions.size==24
    rng=Random.new(seed)
    point={gross:contrast(counts,sessions,1),cancellation:contrast(counts,sessions,2)}
    samples=Hash.new{|h,k|h[k]=[]}
    draws.times do
      selected=Array.new(sessions.size){sessions.fetch(rng.rand(sessions.size))}
      {gross:1,cancellation:2}.each do |type,index|
        contrast(counts,selected,index).each{|name,value|samples[[type,name]]<<value}
      end
    end
    results=point.to_h do |type,parts|
      [type,parts.to_h do |name,v|
        a=samples[[type,name]].sort
        [name,{point:v,lower:a[(draws*0.025).floor],upper:a[(draws*0.975).floor]}]
      end]
    end
    {sessions:sessions.size,draws:draws,contrasts:results}
  end
end
puts JSON.pretty_generate(Rithm210ChurnSessionBootstrap.run(ARGV.fetch(0),
  draws:Integer(ARGV.fetch(1,'20000')))) if $PROGRAM_NAME==__FILE__
