require 'minitest/autorun'
require_relative 'independent_churn_cluster'
class TestRithm210IndependentChurnCluster < Minitest::Test
  M=Rithm210IndependentChurnCluster
  def fixture
    (1..24).to_h do |s|
      [s,{early:{n:1,gross:2,zero:0,cancel:1,loss:0},
          late:{n:1,gross:0,zero:1,cancel:0,loss:0}}]
    end
  end
  def test_moment_calibration_uses_only_gross
    x=M.summary(fixture,(1..24).to_a)
    assert_equal 24,x[:early][:n]
    assert_in_delta Rational(1,3).to_f,x[:early][:epsilon],1e-12
    assert_in_delta 6*(Rational(1,3)).to_f,x[:early][:observed][:gross],1e-12
    assert_equal 0,x[:late][:epsilon]
    assert_equal 1,x[:late][:expected][:zero]
    assert_equal 0,x[:late][:expected][:loss]
  end
  def test_session_resampling_preserves_zero_count
    x=fixture
    x[1][:early]={n:0,gross:0,zero:0,cancel:0,loss:0}
    assert_equal 23,M.summary(x,(1..24).to_a)[:early][:n]
    assert_raises(RuntimeError){M.summary(x,[1])}
  end
  def test_early_real_data_moment_algebra
    row=M.summary(fixture,(1..24).to_a)[:early]
    e=Rational(1,3).to_f
    assert_in_delta (1-e)**6,row[:expected][:zero],1e-12
    assert_in_delta 18*e-6*e*e,row[:expected][:loss],1e-12
  end
end
