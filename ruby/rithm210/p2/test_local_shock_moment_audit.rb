require 'minitest/autorun'
require_relative 'local_shock_moment_audit'
class TestLocalShockMomentAudit < Minitest::Test
  M=Rithm210LocalShockMomentAudit
  def test_zero_shock_zero_predicted_cross
    assert_in_delta 0.0,M.predicted_cross([0.2,0.7],[0.3,0.5],0.0),1e-12
  end
  def test_empty_side_zero_predicted_cross
    assert_in_delta 0.0,M.predicted_cross([],[0.2,0.7],0.6),1e-12
  end
  def test_small_shock_positive
    assert_operator M.predicted_cross([0.2,0.7],[0.3,0.5],0.3),:>,0.0
  end
  def test_mixture_mean_bias_zero_at_zero_shock
    assert_in_delta 0.0,M.mixture_bias([0.2,0.8],0),1e-12
  end
  def test_mixture_mean_bias_sign_symmetry
    assert_in_delta M.mixture_bias([0.2,0.7],0.4),
      M.mixture_bias([0.2,0.7],-0.4),1e-12
  end
  def test_sign_symmetry
    assert_in_delta M.predicted_cross([0.2,0.7],[0.3,0.5],0.3),
      M.predicted_cross([0.2,0.7],[0.3,0.5],-0.3),1e-12
  end
end
