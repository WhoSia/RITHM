# frozen_string_literal: true
require 'json'
module RithmP1P5
 class Court
  attr_reader :memo
  def initialize(horizon:5,boosts:0,setup: :once,objective: :both)
   @h,@budget,@setup,@objective=horizon,boosts,setup,objective;@memo={}
  end
  def reward(a,b)
   case @objective
   when :both then a==2&&b==2 ? 1 : 0
   when :count then (a==2 ? 1 : 0)+(b==2 ? 1 : 0)
   when :a then a==2 ? 1 : 0
   when :b then b==2 ? 1 : 0
   end
  end
  def solve(t=0,a=0,b=0,last=2,outage_used=0,trained=0,spent=0)
   return reward(a,b) if t==@h
   k=[t,a,b,last,outage_used,trained,spent]
   return @memo[k] if @memo.key?(k)
   choices=[0,1].product(spent<@budget ? [0,1] : [0])
   @memo[k]=choices.map{|target,boost|
    (outage_used==1 ? [0] : [0,1]).map{|outage|
     switching=last!=2&&last!=target
     setup_cost=(@setup==:once&&switching&&trained==0)||(@setup==:always&&switching)
     capacity=[0,1+boost-outage-(setup_cost ? 1 : 0)].max
     na,nb=a,b
     na=[2,a+capacity].min if target==0
     nb=[2,b+capacity].min if target==1
     solve(t+1,na,nb,target,outage_used|outage,trained|(switching ? 1 : 0),spent+boost)
    }.min
   }.max
  end
 end
 def self.open_loop(horizon:5,boosts:1)
  plans=[[]]
  horizon.times{plans=plans.flat_map{|plan|
   [0,1].product([0,1]).filter_map{|target,x|plan+[[target,x]] if plan.sum{|_,e|e}+x<=boosts}
  }}
  scenarios=[Array.new(horizon,0)]+horizon.times.map{|at|Array.new(horizon){|t|t==at ? 1 : 0}}
  winners=0
  plans.each{|plan|
   all=scenarios.all?{|outages|
    a=b=0;last=2;trained=0
    plan.each_with_index{|(target,boost),t|
     change=last!=2&&last!=target
     cap=[0,1+boost-outages[t]-(change&&trained==0 ? 1 : 0)].max
     if target==0; a=[2,a+cap].min;else;b=[2,b+cap].min;end
     trained=1 if change;last=target
    }
    a==2&&b==2
   }
   winners+=1 if all
  }
  {guarantee:winners>0 ? 1 : 0,plans:plans.size,scenarios:scenarios.size,winners:winners}
 end
end
if __FILE__==$PROGRAM_NAME
 [5,6].each{|h|[0,1,2].each{|b|
  court=RithmP1P5::Court.new(horizon:h,boosts:b)
  puts JSON.generate(horizon:h,budget:b,adaptive:court.solve,open_loop:RithmP1P5.open_loop(horizon:h,boosts:b),states:court.memo.size)
 }}
end