# frozen_string_literal: true
# Historical information-age opportunity, not randomized treatment effect.
require 'csv'
require 'digest'
module Rithm210R18ObservableAgeSupport
  module_function
  SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'
  def epoch(t)
    return :early if t<=10
    return :middle if t<=29
    :late
  end
  def rows(path)
    raise 'source SHA mismatch' unless Digest::SHA256.file(path).hexdigest==SHA
    groups={}
    CSV.foreach(path,headers:true) do |r|
      s=r.fetch('session').to_i;t=r.fetch('Period').to_i
      next unless r.fetch('trt').to_i==3 && ![2,101].include?(s) && (1..39).cover?(t)
      key=[s,r.fetch('section').to_i,r.fetch('Group').to_i,t]
      n=r.fetch('NumA').to_i;next_n=r.fetch('NumAnext').to_i
      raise 'occupancy range' unless (0..6).cover?(n)&&(0..6).cover?(next_n)
      x=groups[key]||={n:n,next_n:next_n,count:0}
      raise 'inconsistent six-person observation' unless x[:n]==n&&x[:next_n]==next_n
      x[:count]+=1
    end
    raise 'invalid group coverage' unless groups.size==1872&&groups.values.all?{|x|x[:count]==6}
    pairs=[]
    groups.each do |(s,section,g,t),curr|
      next if t==1
      prev=groups.fetch([s,section,g,t-1])
      raise 'nonconsecutive occupancy' unless prev[:next_n]==curr[:n]
      pairs<<{session:s,epoch:epoch(t),unchanged:prev[:n]==curr[:n],
        magnitude:(prev[:n]-curr[:n]).abs}
    end
    raise '1824 required' unless pairs.size==1824
    pairs
  end
  def summarize(pairs)
    raise ArgumentError,'empty source' if pairs.empty?
    scopes={all:pairs,early:pairs.select{|x|x[:epoch]==:early},
      middle:pairs.select{|x|x[:epoch]==:middle},late:pairs.select{|x|x[:epoch]==:late}}
    scopes.reject{|name,a|a.empty?}.to_h do |name,a|
      equal=a.count{|x|x[:unchanged]}
      [name,{pairs:a.size,unchanged:equal,changed:a.size-equal,
        distinct_fraction:(a.size-equal)/a.size.to_f}]
    end
  end
end
if __FILE__==$PROGRAM_NAME
  require 'json'
  puts JSON.pretty_generate(Rithm210R18ObservableAgeSupport.summarize(
    Rithm210R18ObservableAgeSupport.rows(ARGV.fetch(0))))
end
