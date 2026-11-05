require 'minitest/autorun'
require_relative 'group_residual_welfare'
class TestRithm210GroupResidualWelfare < Minitest::Test
  M = Rithm210GroupResidualWelfare
  ROUTES = [1,1,1,1,0,0].freeze
  def test_exact_identity_exhaustive_binary_outcomes
    ps = [0.1,0.2,0.3,0.4,0.5,0.6]
    (0...64).each do |mask|
      ys = 6.times.map { |i| (mask >> i) & 1 }
      a = M.analyze(ROUTES,ys,ps)
      pieces = [:linear_calibration,:diagonal_calibration,:same_route_pair,:opposite_route_pair].sum { |k| a.fetch(k) }
      assert_in_delta a[:welfare_error], pieces, 1e-10
      assert_in_delta a[:observed_loss], 3*a[:signed_net_observed]**2, 1e-10
    end
  end
  def test_perfect_deterministic_forecast_has_zero_residuals
    ys = [1,0,0,1,1,0]
    a = M.analyze(ROUTES,ys,ys)
    [:welfare_error,:linear_calibration,:diagonal_calibration,:same_route_pair,:opposite_route_pair].each do |k|
      assert_in_delta 0,a[k],1e-12
    end
  end
  def test_opposing_residual_products_have_negative_welfare_sign
    a = M.analyze(ROUTES,[1,0,0,0,1,0],[0,0,0,0,0,0])
    assert_in_delta(-6,a[:opposite_route_pair],1e-12)
    assert_equal 0,a[:observed_loss]
  end
  def test_invalid_inputs_fail_closed
    assert_raises(ArgumentError) { M.analyze([1]*6,[0]*6,[0.2]*6) }
    assert_raises(ArgumentError) { M.analyze(ROUTES,[0]*6,[0.2]*5+[1.2]) }
    assert_raises(ArgumentError) { M.analyze(ROUTES,[0]*5+[2],[0.2]*6) }
    assert_raises(ArgumentError) { M.aggregate([]) }
  end
  def test_aggregate_preserves_identity
    a=M.analyze(ROUTES,[0]*6,[0.1]*6)
    b=M.analyze(ROUTES,[1]*6,[0.2]*6)
    x=M.aggregate([a,b])
    assert_equal 2,x[:n]
    sum=[:linear_calibration,:diagonal_calibration,:same_route_pair,:opposite_route_pair].sum { |k| x[k] }
    assert_in_delta x[:welfare_error],sum,1e-10
  end
end
