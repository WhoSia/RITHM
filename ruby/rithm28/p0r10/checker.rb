require 'set'
module RightsCTL
 GRAPH={pending:[:pending,:ordered,:invalid],ordered:[:ordered,:restored],restored:[:restored],invalid:[:invalid]}
 def self.fix(seed,all:false)
  x=seed.to_set
  loop do
   y=x|GRAPH.keys.select{|s|all ? GRAPH[s].all?{|v|x.include?(v)} : GRAPH[s].any?{|v|x.include?(v)}}.to_set
   return x if y==x
   x=y
  end
 end
end
if __FILE__==$PROGRAM_NAME
raise unless RightsCTL.fix([:restored]).include?(:pending)
raise if RightsCTL.fix([:restored],all:true).include?(:pending)
puts 'EF recovered true, AF recovered false at pending'
end
