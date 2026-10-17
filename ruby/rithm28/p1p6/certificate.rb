require_relative 'belief'
module RithmP1P6Certificate
 def self.verify(solver,h:,budget:,lag:)
  return false unless solver.solve
  worlds=[Array.new(h,0)]+h.times.map{|i|Array.new(h){|t|i==t ? 1 : 0}}
  first=(0...worlds.size).map{|i|[i,0,0]}
  count=0;rec=nil
  rec=lambda{|t,states,last,trained,spent|
   if t==h
    raise 'recipient incomplete' unless states.all?{|_,a,b|a==2&&b==2}
    return
   end
   key=[t,states,last,trained,spent];action=solver.witness[key]
   raise 'missing policy certificate' unless action
   who,boost=action;raise 'boost budget exceeded' if spent+boost>budget
   sw=last!=2&&last!=who
   following=states.map{|i,a,b|
    cap=[0,1+boost-worlds[i][t]-(sw&&trained==0 ? 1 : 0)].max
    who==0 ? [i,[2,a+cap].min,b] : [i,a,[2,b+cap].min]
   }
   idx=t+1-lag
   groups=idx>=0 ? following.group_by{|i,_,_|worlds[i][idx]}.values : [following]
   count+=1;groups.each{|g|rec.call(t+1,g,who,trained|(sw ? 1 : 0),spent+boost)}
  }
  rec.call(0,first,2,0,0);count
 end
end
if __FILE__==$PROGRAM_NAME
 [[5,1,4],[5,2,100],[6,0,4],[6,1,100]].each{|h,b,l|
  s=RithmP1P6::Solver.new(horizon:h,budget:b,lag:l)
  puts "PASS H=#{h} boost=#{b} lag=#{l} nodes=#{RithmP1P6Certificate.verify(s,h:h,budget:b,lag:l)}"
 }
end