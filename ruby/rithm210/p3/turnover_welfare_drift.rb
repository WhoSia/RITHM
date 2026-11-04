# frozen_string_literal: true
# Frozen original-source turnover-to-welfare contract.
# Source: SHA-256 d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb.
require 'csv'
require 'digest'
require 'json'

module Rithm210TurnoverWelfareDrift
  module_function
  SOURCE_SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'
  def epoch(t)
    return :early if t<=10
    return :late if t>=30
    :middle
  end
  def score(n,u,d)
    raise ArgumentError,'occupancy' unless n.is_a?(Integer) && n.between?(0,6)
    raise ArgumentError,'turnovers' unless u.is_a?(Integer) && d.is_a?(Integer) &&
      u.between?(0,6-n) && d.between?(0,n)
    change=u-d
    drift=6*(n-4)*change
    quadratic=3*change**2
    current=3*(n-4)**2
    subsequent=3*(n+change-4)**2
    raise 'welfare drift identity' unless subsequent-current==drift+quadratic
    {n:n,u:u,d:d,change:change,drift:drift,quadratic:quadratic,
      current:current,subsequent:subsequent,delta:subsequent-current,
      toward:((n+change-4).abs < (n-4).abs),
      away:((n+change-4).abs > (n-4).abs)}
  end
  def records(csv)
    raise 'unsealed original data' unless Digest::SHA256.file(csv).hexdigest==SOURCE_SHA
    groups=Hash.new{|h,k|h[k]=[]}
    CSV.foreach(csv,headers:true) do |r|
      s=r.fetch('session').to_i;t=r.fetch('trt').to_i;p=r.fetch('Period').to_i
      next unless t.between?(1,3) && s!=2 && s!=101 && p.between?(1,39)
      groups[[s,r.fetch('section').to_i,r.fetch('Group').to_i,p]] << r
    end
    raise 'wrong group panel' unless groups.size==5616 && groups.values.all?{|a|a.size==6}
    groups.map do |(s,section,g,p),people|
      a=people.first
      n=a.fetch('NumA').to_i
      u=people.sum{|r|r.fetch('switchBtoAWill').to_i}
      d=people.sum{|r|r.fetch('switchAtoBWill').to_i}
      raise 'next state mismatch' unless people.all?{|r|
        r['NumA'].to_i==n && r['NumAnext'].to_i==n+u-d}
      {session:s,section:section,group:g,period:p,
        treatment:a.fetch('trt').to_i,epoch:epoch(p),**score(n,u,d)}
    end
  end
  def aggregate(rows)
    raise 'empty' if rows.empty?
    n=rows.size
    keys=[:n,:u,:d,:change,:drift,:quadratic,:current,:subsequent,:delta]
    vals=keys.to_h{|k|["mean_#{k}".to_sym,rows.sum{|r|r.fetch(k)}/n.to_f]}
    vals.merge(n:n,toward_rate:rows.count{|r|r[:toward]}/n.to_f,
      away_rate:rows.count{|r|r[:away]}/n.to_f,
      no_state_change_rate:rows.count{|r|r[:change]==0}/n.to_f)
  end
  def report(csv)
    rs=records(csv)
    {n:rs.size,overall:aggregate(rs),
      treatment_epoch:rs.group_by{|r|[r[:treatment],r[:epoch]]}.
        to_h{|k,a|[k.join('_'),aggregate(a)]},
      current_n_epoch:rs.group_by{|r|[r[:treatment],r[:epoch],r[:n]]}.
        to_h{|k,a|[k.join('_'),aggregate(a)]}}
  end
end
puts JSON.pretty_generate(Rithm210TurnoverWelfareDrift.report(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
