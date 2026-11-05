# frozen_string_literal: true
# RITHM-2.10 R16: analytic witness for 6 independent route Markov actors.
# This elementary exact reduction is prior-art compatible, NOT claimed as novel.
require_relative 'finite_horizon_independent_welfare'
module Rithm210FiniteWelfareClosedForm
  module_function
  def validate(a,horizon)
    q=Rithm210FiniteHorizonIndependentWelfare.rate(a)
    raise ArgumentError,'require 0<a and 2a<=1' unless q.positive? && 2*q<=1
    raise ArgumentError,'horizon positive integer required' unless horizon.is_a?(Integer) && horizon.positive?
    q
  end
  def excess_at(a:,period:)
    raise ArgumentError,'period must be nonnegative integer' unless period.is_a?(Integer) && period>=0
    q=validate(a,1)
    lambda=1-3*q
    4*(1-lambda**(2*period))
  end
  def cumulative(a:,horizon:40)
    q=validate(a,horizon)
    lambda=1-3*q
    r=lambda**2
    4*horizon-4*(1-r**horizon)/(1-r)
  end
end
