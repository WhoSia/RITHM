# frozen_string_literal: true
require 'json'
module RithmP1P4
 class Court
  def initialize(mode:,goal: :count,horizon:5)
   @mode,@goal,@h=mode,goal,horizon;@cache={}
  end
  def score(a,b)
   case @goal
   when :count then (a==2 ? 1 : 0)+(b==2 ? 1 : 0)
   when :a then a==2 ? 1 : 0
   when :b then b==2 ? 1 : 0
   when :both then a==2&&b==2 ? 1 : 0
   when :weighted then (a==2 ? 1 : 0)+3*(b==2 ? 1 : 0)
   end
  end
  def solve(t=0,a=0,b=0,prev=2,used=0,trained=0)
   return score(a,b) if t==@h
   k=[t,a,b,prev,used,trained];return @cache[k] if @cache.key?(k)
   @cache[k]=[0,1].map{|act|
    (used==1 ? [0] : [0,1]).map{|shock|
     switching=prev!=2&&prev!=act
     lost=@mode==:always&&switching||@mode==:learn_once&&switching&&trained==0
     x,y=a,b
     if shock==0&&!lost
      x+=1 if act==0&&x<2
      y+=1 if act==1&&y<2
     end
     solve(t+1,x,y,act,used|shock,trained|(switching ? 1 : 0))
    }.min
   }.max
  end
  def states;@cache.size;end
 end
end
if __FILE__==$PROGRAM_NAME
 [:none,:learn_once,:always].each{|m|[:count,:a,:b,:both,:weighted].each{|g|c=RithmP1P4::Court.new(mode:m,goal:g);puts "#{m} #{g}: #{c.solve} states=#{c.states}"}}
end