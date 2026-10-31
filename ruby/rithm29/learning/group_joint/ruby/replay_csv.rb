# frozen_string_literal: true
require 'csv'
require_relative 'directional_joint'
module RithmDirectionalReplay
  module_function
  ACTOR=%w[trt session section Group ID].freeze
  GROUP=%w[trt session section Group Period].freeze
  def replay(path)
    actors={}
    grouped=Hash.new { |h,k| h[k]=[] }
    CSV.foreach(path,headers:true) do |row|
      actor=ACTOR.map { |k| row.fetch(k).to_i }
      t=row.fetch('Period').to_i
      previous=actors[actor]
      raise ArgumentError,'nonconsecutive actor periods' if previous && t != previous[:period]+1
      if t>1
        raise ArgumentError,'missing historical action' unless previous
        key=GROUP.map { |k| row.fetch(k).to_i }
        grouped[key]<<[previous[:action],row.fetch('RouteA').to_i,Float(row.fetch('p_ewa'))]
      end
      actors[actor]={action:row.fetch('RouteA').to_i,period:t}
    end
    grouped.map do |key,people|
      raise ArgumentError,'group not 6' unless people.size==6
      prev=people.map(&:first)
      route=people.map { |p| p[1] }
      probabilities=people.map(&:last)
      u=(0...6).count { |i| prev[i]==0 && route[i]==1 }
      d=(0...6).count { |i| prev[i]==1 && route[i]==0 }
      joint=RithmDirectionalJoint.distribution(previous:prev,probabilities:probabilities)
      stats=RithmDirectionalJoint.expectation(joint)
      [*key,u,d,u+d,(u-d).abs,(u>0 && d>0 ? 1 : 0),RithmDirectionalJoint.probability(joint,u,d),stats[:cancellation],stats[:gross],stats[:net_abs]]
    end.sort_by { |z| z[0,5] }
  end
end
if $PROGRAM_NAME==__FILE__
  abort 'usage: ruby replay_csv.rb predictions.csv out.csv' unless ARGV.size==2
  out=RithmDirectionalReplay.replay(ARGV[0])
  CSV.open(ARGV[1],'w') do |csv|
    csv<<%w[trt session section Group Period U D S absnet cancel p_ud p_cancel e_switch e_absnet]
    out.each { |r| csv<<r }
  end
  warn "replayed #{out.length} group-periods"
end
