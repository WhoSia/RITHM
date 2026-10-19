# frozen_string_literal: true
require_relative 'correspondence'
module Rithm29OnePeriodRegions
 module_function
 C=Rithm29Correspondence
 # Each deviation inequality is exactly alpha+beta*F+gamma*k>=0 (L held fixed).
 # F prices the full READ/READ/XOR program; STOP0 and STOP1 remain free.
 def inequalities(previous:,wrong:2)
  zero=C::STATES.to_h{|s|[s,[0,0]]}
  basis=[[0,0],[1,0],[0,1]].map{|fee,k|
    C::PROGRAMS.product(C::PROGRAMS).to_h{|pair|
      rows=C::WORLDS.map{|w|C.outcome(pair,previous,w,fee:fee,switch:k,wrong:wrong)[1]}
      [pair,2.times.map{|i|rows.sum{|v|v[i]}/Rational(4)}]
    }
  }
  C::PROGRAMS.product(C::PROGRAMS).to_h do |pair|
   constraints=2.times.flat_map do |i|
    C::PROGRAMS.reject{|p|p==pair[i]}.map do |alt|
     rival=pair.dup;rival[i]=alt
     y=basis.map{|table|table[rival][i]-table[pair][i]}
     {actor:i,alternative:alt,constant:y[0],fee_coefficient:y[1]-y[0],switch_coefficient:y[2]-y[0]}
    end
   end
   [pair,constraints]
  end
 end
 def equilibria(previous:,fee:,switch:,wrong:2)
  inequalities(previous:previous,wrong:wrong).select{|_,clauses|
   clauses.all?{|c|c[:constant]+c[:fee_coefficient]*fee+c[:switch_coefficient]*switch>=0}
  }.keys
 end
end
