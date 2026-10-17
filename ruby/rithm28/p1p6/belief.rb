# frozen_string_literal: true
# Observation legal: only w[t-lag] received at decision t. No progress oracle.
module RithmP1P6
 class Solver
  attr_reader :memo,:witness
  def initialize(horizon:5,budget:1,lag:1)
   @h,@budget,@lag=horizon,budget,lag
   @worlds=[Array.new(@h,0)]+@h.times.map{|i|Array.new(@h){|j|i==j ? 1 : 0}}
   @memo={};@witness={}
  end
  def solve
   states=(0...@worlds.size).map{|i|[i,0,0]}
   decide(0,states,2,0,0)
  end
  def decide(t,states,last,trained,spent)
   return states.all?{|_,a,b|a==2&&b==2} if t==@h
   key=[t,states,last,trained,spent]
   return @memo[key] if @memo.key?(key)
   [0,1].each do |who|
    (0..(spent<@budget ? 1 : 0)).each do |boost|
     switched=last!=2&&last!=who
     following=states.map{|i,a,b|
      cap=[0,1+boost-@worlds[i][t]-(switched&&trained==0 ? 1 : 0)].max
      who==0 ? [i,[2,a+cap].min,b] : [i,a,[2,b+cap].min]
     }
     idx=t+1-@lag
     groups=idx>=0 ? following.group_by{|i,_,_|@worlds[i][idx]}.values : [following]
     if groups.all?{|group|decide(t+1,group,who,trained|(switched ? 1 : 0),spent+boost)}
      @memo[key]=true;@witness[key]=[who,boost];return true
     end
    end
   end
   @memo[key]=false
  end
 end
end
if __FILE__==$PROGRAM_NAME
 [5,6].each{|h|[1,2,3,4,100].each{|lag|
  budgets=(0..2).find{|b|RithmP1P6::Solver.new(horizon:h,budget:b,lag:lag).solve}
  puts "H=#{h} lag=#{lag} minimum_boost=#{budgets}"
 }}
end