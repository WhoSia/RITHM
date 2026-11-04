require 'minitest/autorun'
require_relative 'activity_mixture'
class TestRithm210ActivityMixture < Minitest::Test
  M = Rithm210ActivityMixture
  def law
    { [0, 0] => Rational(1, 5), [1, 0] => Rational(1, 5),
      [0, 1] => Rational(1, 5), [1, 1] => Rational(2, 5) }
  end
  def test_exact_probability_mass_and_joint_events
    f = M.freeze(law, Rational(1, 4))
    assert_equal Rational(2, 5), f[[0, 0]]
    assert_equal Rational(3, 10), f[[1, 1]]
    assert_equal 1, f.values.sum
    assert_equal Rational(3, 10), M.event_metrics(f)[:cancel]
  end
  def test_exact_n4_congestion_and_activity_restrictions
    r = M.restrictions(law, target_zero: Rational(2, 5))
    assert r[:feasible]
    assert_equal Rational(1, 4), r[:z]
    assert_equal Rational(3, 4) * r[:baseline][:gross], r[:counterfactual][:gross]
    assert_equal Rational(3, 4) * r[:baseline][:next_excess], r[:counterfactual][:next_excess]
    assert_equal Rational(3, 4) * r[:baseline][:cancel], r[:counterfactual][:cancel]
  end
  def test_early_ssm5_has_no_freeze_only_solution
    assert_nil M.freeze_required(base_zero: 0.60177773, target_zero: 34.0 / 154)
    z = M.freeze_required(base_zero: 0.50317535, target_zero: 150.0 / 257)
    assert_in_delta 0.161994, z, 0.002
  end
  def test_nonoptimal_welfare_drift_scaled_not_next_cost
    a = M.event_metrics(law, current_a: 3)
    b = M.event_metrics(M.freeze(law, Rational(1, 4)), current_a: 3)
    assert_equal Rational(3, 4) * a[:drift], b[:drift]
    assert_equal Rational(1, 4) * 3 + Rational(3, 4) * a[:next_excess], b[:next_excess]
  end
  def test_reject_invalid_and_infeasible_events
    assert_raises(ArgumentError) { M.freeze({[0, 0] => 0.4}, 0.1) }
    assert_raises(ArgumentError) { M.freeze(law, -0.1) }
    assert_raises(ArgumentError) { M.event_metrics({[3, 0] => 1}, current_a: 4) }
  end
end
