# frozen_string_literal: true
# Closed rational formula obtained by exact elimination of the six transient
# states of the oracle six-person mixed synchronization Markov chain.
require_relative 'mixed_clock_chain'
module Rithm210MixedClockTheorem
  module_function
  def closed_form_t3(sync:)
    s=Rithm210MixedClockChain.probability(sync,:sync)
    raise ArgumentError,'nonabsorbing at s=1' if s==1
    numerator=2*(s+2)*(s+5)*(5*s*s-12*s-5)
    denominator=5*(s-1)**2*(5*s+1)*(2*s**3-9*s*s+11*s-10)
    numerator/denominator
  end
  def leading_constant
    Rational(12,5)
  end
  def exact_limit_gap(sync:)
    s=Rithm210MixedClockChain.probability(sync,:sync)
    (1-s)**2*closed_form_t3(sync:s)-leading_constant
  end
end
