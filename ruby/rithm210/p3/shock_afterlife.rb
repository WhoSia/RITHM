# frozen_string_literal: true
# Shock afterlife in the exact six-person game, with one exogenous mistaken move
# out of the socially optimal and pure-Nash count n=4, then perfect strict best responses.
# A reference counterexample: no novel general theorem is asserted.
require_relative 'adjustment_clocks'
module Rithm210ShockAfterlife
  module_function
  G=Rithm210AtomicNash
  C=Rithm210AdjustmentClocks

  def discounted_sync(post_shock_n:,beta:)
    validate(post_shock_n,beta)
    b=Rational(beta)
    # n=3 -> 6 -> 0 -> 6; n=5 -> 0 -> 6 -> 0
    first=post_shock_n==3 ? 6 : 0
    second=post_shock_n==3 ? 0 : 6
    initial=G.group_cost(post_shock_n)-G.group_cost(4)
    a=G.group_cost(first)-G.group_cost(4)
    c=G.group_cost(second)-G.group_cost(4)
    initial+(a*b+c*b*b)/(1-b*b)
  end

  def discounted_async_random_actor(post_shock_n:,beta:)
    validate(post_shock_n,beta)
    b=Rational(beta)
    n=post_shock_n
    current=G.group_cost(n)-G.group_cost(4)
    # Each period, one of the 6 actors is selected uniformly.
    # The action type that can profitably correct n=3 is B (3 of 6);
    # for n=5 it is A (5 of 6).
    move_prob=n==3 ? Rational(3,6) : Rational(5,6)
    current/(1-b*(1-move_prob))
  end

  def validate(n,beta)
    raise ArgumentError,'single departure only n=3 or 5' unless [3,5].include?(n)
    b=Rational(beta)
    raise ArgumentError,'discount must lie in [0,1)' unless b>=0 && b<1
  end

  def example(beta:Rational(9,10))
    [3,5].to_h do |n|
      [n,{first_synchronous:C.synchronous(n),
        sync_discounted_excess:discounted_sync(post_shock_n:n,beta:beta),
        asynchronous_discounted_excess:discounted_async_random_actor(post_shock_n:n,beta:beta)}]
    end
  end
end
