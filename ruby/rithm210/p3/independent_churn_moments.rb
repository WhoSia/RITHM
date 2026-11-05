# frozen_string_literal: true
# Homogeneous, independent six-person switching benchmark at current n=4.
# Calibrates only to mean gross churn, then makes 3 FREE predictions.
# It is an analyst-level descriptive diagnostic, not a participant information model.
module Rithm210IndependentChurnMoment
  module_function

  def probability(x)
    v=Float(x)
    raise ArgumentError,'epsilon outside [0,1]' unless v.finite? && v.between?(0,1)
    v
  end

  def choose(n,k)
    return 0 if k<0 || k>n
    (1..k).reduce(1){|a,i|a*(n-i+1)/i}
  end

  def from_gross(mean_gross)
    g=Float(mean_gross)
    raise ArgumentError,'mean gross outside [0,6]' unless g.finite? && g.between?(0,6)
    epsilon=g/6.0
    no_switch=(1-epsilon)**6
    cancellation=(1..2).sum do |k|
      choose(2,k)*choose(4,k)*(epsilon**(2*k))*((1-epsilon)**(6-2*k))
    end
    next_excess=18*epsilon-6*epsilon*epsilon
    {epsilon:epsilon,mean_gross:g,no_switch:no_switch,
     cancellation:cancellation,next_excess:next_excess}
  end

  def exact_distribution(epsilon)
    p=probability(epsilon)
    law={}
    (0..2).each do |u|
      (0..4).each do |d|
        law[[u,d]]=choose(2,u)*choose(4,d)*p**(u+d)*(1-p)**(6-u-d)
      end
    end
    raise 'probability mass' unless (law.values.sum-1).abs<1e-12
    law
  end

  def assess(mean_gross:,observed_zero:,observed_cancel:,observed_next_excess:)
    b=from_gross(mean_gross)
    {baseline:b,residuals:{
      zero:observed_zero-b[:no_switch],
      cancellation:observed_cancel-b[:cancellation],
      next_excess:observed_next_excess-b[:next_excess]}}
  end
end
