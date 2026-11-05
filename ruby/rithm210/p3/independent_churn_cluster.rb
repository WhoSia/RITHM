# frozen_string_literal: true
# Original SHA-verified experiment; whole-session bootstrap with epsilon refit each draw.
# No human-level CSV committed. Exploratory same-data moment restrictions, not holdout.
require 'csv'
require 'digest'
require 'json'
module Rithm210IndependentChurnCluster
  module_function
  SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'
  KEYS=[:gross,:zero,:cancel,:loss].freeze
  def source(csv)
    raise 'source SHA failed' unless Digest::SHA256.file(csv).hexdigest==SHA
    grouped=Hash.new{|h,k|h[k]=[]}
    CSV.foreach(csv,headers:true) do |r|
      sess=r['session'].to_i; trt=r['trt'].to_i; period=r['Period'].to_i
      next unless (1..3).cover?(trt) && sess!=2 && sess!=101 && (1..39).cover?(period)
      grouped[[sess,r['section'].to_i,r['Group'].to_i,period]] << r
    end
    raise "bad group count #{grouped.size}" unless grouped.size==5616
    sessions=grouped.keys.map(&:first).uniq.sort
    raise 'not 24 sessions' unless sessions.size==24
    cell=sessions.to_h{|s|[s,{early:Hash.new(0),late:Hash.new(0)}]}
    grouped.each do |(s,sect,g,t),people|
      raise 'wrong players' unless people.size==6
      next unless people.first['trt'].to_i==3 && people.first['NumA'].to_i==4 && (t<=10 || t>=30)
      u=people.sum{|r|r['switchBtoAWill'].to_i}
      d=people.sum{|r|r['switchAtoBWill'].to_i}
      raise 'bad implied occupancy' unless 4+u-d==people.first['NumAnext'].to_i
      a=cell.fetch(s).fetch(t<=10 ? :early : :late)
      a[:n]+=1
      a[:gross]+=u+d
      a[:zero]+=1 if u+d==0
      a[:cancel]+=1 if u>0 && u==d
      a[:loss]+=3*(u-d)**2
    end
    raise 'bad support' unless [:early,:late].map{|ep|sessions.sum{|s|cell[s][ep][:n]}}==[154,257]
    [sessions,cell]
  end
  def summary(totals,chosen)
    [:early,:late].to_h do |ep|
      n=chosen.sum{|s|totals.fetch(s).fetch(ep)[:n]}
      raise 'zero support in bootstrap' if n==0
      g=chosen.sum{|s|totals.fetch(s).fetch(ep)[:gross]}.fdiv(n)
      observed=KEYS.to_h{|k|[k,chosen.sum{|s|totals.fetch(s).fetch(ep)[k]}.fdiv(n)]}
      e=g/6.0
      expected={gross:g,zero:(1-e)**6,
        cancel:8*e**2*(1-e)**4+6*e**4*(1-e)**2,
        loss:18*e-6*e**2}
      [ep,{n:n,epsilon:e,observed:observed,expected:expected,
        residuals:KEYS.to_h{|k|[k,observed[k]-expected[k]]}}]
    end
  end
  def analyze(csv,draws:20_000,seed:20261105)
    sessions,totals=source(csv)
    point=summary(totals,sessions)
    rng=Random.new(seed)
    boots=[:early,:late].to_h{|ep|[ep,KEYS.to_h{|k|[k,[]]}]}
    draws.times do
      selected=Array.new(sessions.size){sessions.fetch(rng.rand(sessions.size))}
      sample=summary(totals,selected)
      boots.each do |ep,v|
        KEYS.each{|key|v[key]<<sample[ep][:residuals][key]}
      end
    end
    ci=boots.to_h do |ep,groups|
      [ep,groups.to_h do |k,values|
        sorted=values.sort
        [k,[sorted[(draws*0.025).floor],sorted[(draws*0.975).floor]]]
      end]
    end
    {groups:5616,sessions:24,draws:draws,point:point,ci:ci,
      scope:'descriptive cluster-resampling, epsilon re-estimated each bootstrap; NOT heldout'}
  end
end
puts JSON.pretty_generate(Rithm210IndependentChurnCluster.analyze(ARGV.fetch(0),
  draws:Integer(ARGV.fetch(1,'20000')))) if $PROGRAM_NAME==__FILE__
