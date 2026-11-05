# frozen_string_literal: true
require_relative 'r19_partial_welfare'
# Exact rational value of a noisy observation about hidden actor0 identity.
module Rithm210R19InformationValue
  module_function
  Base=Rithm210R19PartialWelfare
  def posterior_prob_a(signal:,accuracy:,prior:1.to_r/2)
    raise ArgumentError,'signal A/B' unless [:a,:b].include?(signal)
    raise ArgumentError,'rational accuracy/prior' unless [accuracy,prior].all?{|x|x.is_a?(Rational)&&x.between?(0,1)}
    l_a=signal==:a ? accuracy : 1-accuracy
    l_b=signal==:b ? accuracy : 1-accuracy
    evidence=prior*l_a+(1-prior)*l_b
    raise ArgumentError,'zero evidence' if evidence.zero?
    prior*l_a/evidence
  end
  def actor0_costs(horizon:40)
    baseline=Base.counterexample(horizon:horizon)[:baseline][:minimum]
    a,b=Base.toggle_actor_zero
    v=Base.values(p_a:a,p_b:b,horizon:horizon)
    groups=(0...64).select{|m|Base.occupancy(m)==3}.group_by{|m|m&1}
    c_b=groups.fetch(0).map{|m|v[m]}.uniq
    c_a=groups.fetch(1).map{|m|v[m]}.uniq
    raise 'unknown identity effect' unless c_a.size==1&&c_b.size==1
    {a:c_a.first,b:c_b.first,baseline:baseline}
  end
  def expected_intervention_cost(prob_actor0_a:,horizon:40)
    raise ArgumentError,'posterior rational [0,1]' unless prob_actor0_a.is_a?(Rational)&&prob_actor0_a.between?(0,1)
    c=actor0_costs(horizon:horizon)
    prob_actor0_a*c[:a]+(1-prob_actor0_a)*c[:b]
  end
  def decision_given_signal(signal:,accuracy:,horizon:40)
    posterior=posterior_prob_a(signal:signal,accuracy:accuracy)
    c=actor0_costs(horizon:horizon)
    treated=posterior*c[:a]+(1-posterior)*c[:b]
    {posterior_a:posterior,treat_cost:treated,baseline_cost:c[:baseline],
     choose_treatment:treated<c[:baseline],optimal_cost:[treated,c[:baseline]].min}
  end
  def ex_ante_value(accuracy:,horizon:40)
    raise ArgumentError,'accuracy rational [1/2,1]' unless accuracy.is_a?(Rational)&&accuracy.between?(1.to_r/2,1)
    a=decision_given_signal(signal: :a,accuracy:accuracy,horizon:horizon)
    b=decision_given_signal(signal: :b,accuracy:accuracy,horizon:horizon)
    baseline=actor0_costs(horizon:horizon)[:baseline]
    expected=(a[:optimal_cost]+b[:optimal_cost])/2
    {accuracy:accuracy,without_identity_cost:baseline,
     with_signal_optimal_cost:expected,information_value:baseline-expected,
     signal_a:a,signal_b:b}
  end
end
