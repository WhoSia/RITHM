# frozen_string_literal: true
require_relative '../p2/correspondence'
# Exact 2x2 support mixed Nash in 3x3 stage game, given a fixed continuation.
# Comprehensive supports of size >2 and asymmetric support pairs NOT certified.
module Rithm29MixedSupport
 module_function
 C=Rithm29Correspondence
 def payoffs(future,prev,fee:,switch:,wrong:)
   C::PROGRAMS.product(C::PROGRAMS).each_with_object({}) do |pair,rows|
     costs=[0,0]
     C::WORLDS.each do |w|
       actions,now=C.outcome(pair,prev,w,fee:fee,switch:switch,wrong:wrong)
       2.times{|i|costs[i]+=Rational(now[i]+future.fetch(actions)[i],4)}
     end
     rows[pair]=costs
   end
 end
 def symmetric_two_support(future,prev:,fee:,switch:,wrong:2)
   raise ArgumentError unless prev[0]==prev[1]
   table=payoffs(future,prev,fee:fee,switch:switch,wrong:wrong)
   out=[]
   C::PROGRAMS.combination(2) do |a,b|
     # Requires symmetry of continuation payoffs under agent permutation.
     next unless C::PROGRAMS.product(C::PROGRAMS).all?{|x,y|table[[x,y]][0]==table[[y,x]][1]}
     d0=table[[b,a]][0]-table[[a,a]][0]
     d1=table[[b,b]][0]-table[[a,b]][0]
     next if d0==d1
     x= -d0/Rational(d1-d0)
     next unless x>0&&x<1
     costs=C::PROGRAMS.map{|alt|(1-x)*table[[alt,a]][0]+x*table[[alt,b]][0]}
     base=costs[C::PROGRAMS.index(a)]
     next unless base==costs[C::PROGRAMS.index(b)] && costs.all?{|c|c>=base}
     joint=C::PROGRAMS.product(C::PROGRAMS).sum do |pair|
       pa=pair[0]==a ? 1-x : pair[0]==b ? x : 0
       pb=pair[1]==a ? 1-x : pair[1]==b ? x : 0
       pa*pb*table[pair].sum
     end
     out<<{support:[a,b],probability_b:x,individual:base,social:joint}
   end
   out
 end
end
