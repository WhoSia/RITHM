# frozen_string_literal: true
require 'json'
module RithmP1P3
 H=5
 class Court
  def initialize(setup:false,objective: :count)
   @setup,@objective=setup,objective;@memo={}
  end
  def score(a,b,ta,tb)
   case @objective
   when :count then (a==2 ? 1 : 0)+(b==2 ? 1 : 0)
   when :deadline then (ta&&ta<=3 ? 1 : 0)+(tb&&tb<=3 ? 1 : 0)
   when :weighted then (a==2 ? 1 : 0)+3*(b==2 ? 1 : 0)
   when :min_group then [(a==2 ? 1 : 0),(b==2 ? 1 : 0)].min
   else raise @objective.to_s
   end
  end
  def value(t=0,a=0,b=0,prev=2,used=0,ta=nil,tb=nil)
   return score(a,b,ta,tb) if t==H
   key=[t,a,b,prev,used,ta,tb];return @memo[key] if @memo.key?(key)
   best=[0,1].map{|action|
    shocks=used==1 ? [0] : [0,1]
    shocks.map{|shock|
     x,y=a,b
     if shock==0&&(!@setup||prev==2||prev==action)
      x+=1 if action==0&&x<2
      y+=1 if action==1&&y<2
     end
     value(t+1,x,y,action,used|shock,ta||(x==2 ? t+1 : nil),tb||(y==2 ? t+1 : nil))
    }.min
   }.max
   @memo[key]=best
  end
  def result;{setup:@setup,objective:@objective,guarantee:value,states:@memo.length};end
 end
 def self.results
  [false,true].product([:count,:deadline,:weighted,:min_group]).map{|s,o|Court.new(setup:s,objective:o).result}
 end
end
puts JSON.pretty_generate(RithmP1P3.results) if __FILE__==$PROGRAM_NAME
