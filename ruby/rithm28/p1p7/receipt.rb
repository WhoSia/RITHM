# frozen_string_literal: true
require 'json'
module RithmP1P7
 Event=Struct.new(:event,:published,:received,:certified,keyword_init:true)
 class Contract
  attr_reader :events
  def initialize(h:,pattern:,certified:true)
   @events=Array.new(h){|e|
    r=case pattern
    when :lag1 then e+1
    when :lag4 then e+4
    when :blackout then h+5
    when :reorder then e==0 ? 4 : (e==1 ? 2 : e+2)
    when :late then e==0 ? 5 : e+1
    else raise ArgumentError
    end
    Event.new(event:e,published:e+1,received:r,certified:certified)
   }
   validate!
  end
  def validate!
   @events.each{|x|raise 'clock order' if x.published<x.event+1||x.received<x.published}
  end
  def observation(t,w)
   @events.filter{|x|x.certified&&x.received==t}.map{|x|[x.event,w[x.event]]}
  end
 end
 class Solver
  attr_reader :policy
  def initialize(h:,budget:,contract:)
   @h,@budget,@contract=h,budget,contract
   @worlds=[Array.new(h,0)]+h.times.map{|i|Array.new(h){|j|i==j ? 1 : 0}}
   @memo={};@policy={}
  end
  def solve
   rec(0,@worlds.each_index.map{|i|[i,0,0]},2,0,0)
  end
  def rec(t,records,last,trained,spent)
   return records.all?{|_,a,b|a==2&&b==2} if t==@h
   key=[t,records,last,trained,spent]
   return @memo[key] if @memo.key?(key)
   [0,1].each{|who|(0..(spent<@budget ? 1 : 0)).each{|boost|
    sw=last!=2&&last!=who
    nxt=records.map{|i,a,b|
     cap=[0,1+boost-@worlds[i][t]-(sw&&trained==0 ? 1 : 0)].max
     who==0 ? [i,[2,a+cap].min,b] : [i,a,[2,b+cap].min]
    }
    groups=nxt.group_by{|i,_,_|@contract.observation(t+1,@worlds[i])}.values
    if groups.all?{|g|rec(t+1,g,who,trained|(sw ? 1 : 0),spent+boost)}
     @memo[key]=true;@policy[key]=[who,boost];return true
    end
   }}
   @memo[key]=false
  end
  def replay!
   raise 'no winning policy' unless solve
   walk=nil;visited=0
   walk=lambda{|t,rs,last,trained,spent|
    if t==@h
     raise 'recipient incomplete' unless rs.all?{|_,a,b|a==2&&b==2}
     next
    end
    who,boost=@policy.fetch([t,rs,last,trained,spent])
    raise 'budget' if spent+boost>@budget
    sw=last!=2&&last!=who
    nxt=rs.map{|i,a,b|
     cap=[0,1+boost-@worlds[i][t]-(sw&&trained==0 ? 1 : 0)].max
     who==0 ? [i,[2,a+cap].min,b] : [i,a,[2,b+cap].min]
    }
    visited+=1
    nxt.group_by{|i,_,_|@contract.observation(t+1,@worlds[i])}.each_value{|g|walk.call(t+1,g,who,trained|(sw ? 1 : 0),spent+boost)}
   }
   walk.call(0,@worlds.each_index.map{|i|[i,0,0]},2,0,0)
   visited
  end
 end
 def self.study
  [5,6].flat_map{|h|[:lag1,:lag4,:reorder,:late,:blackout].map{|p|
   c=Contract.new(h:h,pattern:p)
   b=(0..2).find{|n|Solver.new(h:h,budget:n,contract:c).solve}
   {h:h,pattern:p,minimum:b,certificate_nodes:Solver.new(h:h,budget:b,contract:c).replay!}
  }}
 end
end
puts JSON.pretty_generate(RithmP1P7.study) if __FILE__==$PROGRAM_NAME
