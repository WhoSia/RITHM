# frozen_string_literal: true
# Identifiability of clock mixing when complete pre/post occupancies are observed.
# Applies ONLY to the error-free oracle-response model, not the original experiment.
require_relative 'mixed_clock_chain'
module Rithm210MixedClockIdentification
  module_function
  M=Rithm210MixedClockChain
  def types(current:)
    Rithm210AtomicNash.group_cost(current)
    sync=Rithm210AdjustmentClocks.synchronous(current)
    async=M.transition(current,sync:0).select{|_,p|p>0}.keys
    {sync_next:sync,async_next:async,disjoint:!async.include?(sync)}
  end
  def identified_clock(current:,next_count:)
    Rithm210AtomicNash.group_cost(next_count)
    row=types(current:current)
    return :unidentified if current==4 && next_count==4
    return :synchronous if next_count==row[:sync_next] && row[:disjoint]
    return :asynchronous if row[:async_next].include?(next_count) && row[:disjoint]
    :outside_model_support
  end
  def fisher_information_per_observation(current:,sync:)
    Rithm210AtomicNash.group_cost(current)
    s=M.probability(sync,:sync)
    return 0 if current==4
    raise ArgumentError,'regular Fisher info requires 0<s<1' unless s>0 && s<1
    1/(s*(1-s))
  end
end
