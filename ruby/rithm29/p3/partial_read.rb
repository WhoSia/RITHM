# frozen_string_literal: true
require_relative '../p2/correspondence'
# Expanded ISA partial READ_X then constant action. In this explicitly
# independent fair-bit world, the first bit is independent of parity.
# Here READ_X does not change action and costs positive r: strictly dominated.
# This result does NOT cover conditional routing on X, shared probes or
# correlated environmental bits.
module Rithm29PartialRead
 module_function
 def check(read_fee:,full_fee:,switch:,wrong:2,prev:[0,0])
   raise ArgumentError unless [read_fee,full_fee,switch,wrong].all?{|x|x>=0}
   pairs=Rithm29Correspondence::PROGRAMS.product(Rithm29Correspondence::PROGRAMS)
   rows=pairs.flat_map do |pair|
     2.times.map do |i|
       base=Rithm29Correspondence::WORLDS.sum do |w|
         _a,c=Rithm29Correspondence.outcome(pair,prev,w,fee:full_fee,switch:switch,wrong:wrong)
         Rational(c[i],4)
       end
       # Partial read plus identical fixed route has no behavioral effect.
       {policy_pair:pair,player:i,base:base,partial_read_same_route:base+read_fee}
     end
   end
   {rows:rows,dominated:read_fee>0 && rows.all?{|x|x[:partial_read_same_route]>x[:base]},
    qualification:'partial read followed by unchanged fixed route only'}
 end
end
