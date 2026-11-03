# frozen_string_literal: true
# RITHM-2.10 P0: a shared unobserved shock creates positive joint-turnover
# residual dependence despite conditional independence of every actor.
module Rithm210LatentShock
  module_function
  def moments(n_a:, n_b:, base:, delta:)
    raise ArgumentError, 'counts must be nonnegative' unless [n_a,n_b].all?{|n| n.is_a?(Integer) && n>=0}
    raise ArgumentError, 'invalid mixture probabilities' unless base-delta>=0 && base+delta<=1
    eu=n_b*base
    ed=n_a*base
    eud=n_a*n_b*((base+delta)**2+(base-delta)**2)/2
    {eu:eu,ed:ed,cross:eud-eu*ed}
  end
  def independent_conditional_given_z?(base:,delta:)
    [base-delta,base+delta].all?{|p|p.between?(0,1)}
  end
end
if __FILE__==$PROGRAM_NAME
  require 'json'
  result=Rithm210LatentShock.moments(n_a:3,n_b:3,base:Rational(1,2),delta:Rational(3,40))
  puts JSON.pretty_generate(result.transform_values{|v|v.to_f})
end
