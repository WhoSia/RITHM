# frozen_string_literal: true
require_relative 'r19_partial_welfare'
# Exact closed-form sharp width: an identified welfare functional may
# coexist with unidentified individual composition.
module Rithm210R19IdentificationPhase
  module_function
  M=Rithm210R19PartialWelfare
  def closed_form(n:,horizon:)
    raise ArgumentError,'occupancy 1..5' unless n.is_a?(Integer)&&n.between?(1,5)
    raise ArgumentError,'positive horizon' unless horizon.is_a?(Integer)&&horizon.positive?
    steps=horizon/2
    c=n*n+2*(6-n)**2
    plus=(n+1)**2+2*(5-n)**2
    minus=(n-1)**2+2*(7-n)**2
    vals=[horizon*c+steps*(plus-c),horizon*c+steps*(minus-c)]
    {minimum:vals.min,maximum:vals.max,width:steps*12*(n-4).abs}
  end
  def independently_check(n:,horizon:)
    pa,pb=M.toggle_actor_zero
    exact=M.envelope(observed_n:n,p_a:pa,p_b:pb,horizon:horizon)
    analytic=closed_form(n:n,horizon:horizon)
    raise 'closed form differs from Markov DP' unless
      [:minimum,:maximum,:width].all?{|k|exact[k]==analytic[k]}
    {n:n,horizon:horizon,**analytic}
  end
end
