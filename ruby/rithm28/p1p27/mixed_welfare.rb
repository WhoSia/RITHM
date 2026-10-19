# frozen_string_literal: true
require_relative '../p1p26/full_mixed'
module RithmMixedWelfare
 module_function
 def decomposition(q:)
   r=RithmFullMixedCourt.certificate(q:q)
   x=r.fetch('x')
   # No acquire: 6; one acquire: 47/8 + q; two acquire: 31/4 + 2q.
   base=6
   single=Rational(47,8)+q
   both=Rational(31,4)+2*q
   total=(1-x)**2*base+2*x*(1-x)*single+x*x*both
   raise 'cross-check failed' unless total==r.fetch('expected_social_cost')
   raise 'mixed equilibrium welfare identity fails' unless total==6
   {'q'=>q,'x'=>x,'without_information'=>base,'one_inspector'=>single,
    'two_inspectors'=>both,'mixed_welfare'=>total,
    'identity'=>'6+2*x*(q-1/8)+2*x*x = 6 at x=1/8-q',
    'all_mixed_nash_characterized'=>false}
 end
end
