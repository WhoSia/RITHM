require 'minitest/autorun'
require_relative 'session_weighted_bootstrap'
class SessionWeightedBootstrapTest < Minitest::Test
  B = RithmSessionWeightedBootstrap
  def test_unequal_session_sizes_change_estimand
    rows = [{n:1,baseline:1.0,candidate:0.0},{n:3,baseline:1.0,candidate:2.0}]
    assert_in_delta 0.5,B.estimate(rows),1e-12
    assert_in_delta 0.0,B.estimate(rows,estimand: :equal_session),1e-12
  end
  def test_zero_loss_difference_and_seed
    rows = [{n:117,baseline:0.3,candidate:0.3},{n:351,baseline:0.9,candidate:0.9}]
    a = B.interval(rows,draws:200)
    assert_equal a,B.interval(rows,draws:200)
    assert_equal 0.0,a[:mean]
    assert_equal 0.0,a[:lower]
    assert_equal 0.0,a[:upper]
  end
  def test_reject_bad_sessions
    assert_raises(ArgumentError) { B.estimate([{n:0,baseline:0.1,candidate:0.2}]) }
    assert_raises(ArgumentError) { B.interval([{n:1,baseline:0.1,candidate:Float::NAN}]) }
    assert_raises(ArgumentError) { B.interval([{n:1,baseline:0.1,candidate:0.2}],draws:1) }
  end
end
