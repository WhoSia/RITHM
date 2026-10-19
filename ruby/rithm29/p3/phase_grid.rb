# frozen_string_literal: true
require_relative '../p2/correspondence'
module Rithm29PhaseGrid
 module_function
 def scan(horizon:2,fees:[0,Rational(1,2),1,Rational(3,2)],switches:[0,Rational(1,2),1],wrong:2,limit:100_000)
  fees.product(switches).map do |fee,k|
   r=Rithm29Correspondence.enumerate(horizon:horizon,fee:fee,switch:k,wrong:wrong,limit:limit)
   {fee:fee,switch:k,complete:r[:complete],policies:r[:equilibrium_policies],
    minimum:r[:minimum],maximum:r[:maximum],distinct:r[:welfare_values]&.length}
  end
 end
end
