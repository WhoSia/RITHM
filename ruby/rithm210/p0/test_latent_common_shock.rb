require 'minitest/autorun'
require_relative 'latent_common_shock'
class Rithm210LatentShockTest < Minitest::Test
  def test_positive_residual_without_interaction
    m=Rithm210LatentShock.moments(n_a:3,n_b:3,base:Rational(1,2),delta:Rational(3,40))
    assert_equal Rational(3,2),m[:eu]
    assert_equal Rational(3,2),m[:ed]
    assert_equal Rational(81,1600),m[:cross]
  end
  def test_no_shock_zero_cross_moment
    assert_equal 0,Rithm210LatentShock.moments(n_a:3,n_b:3,base:Rational(1,2),delta:0)[:cross]
  end
  def test_zero_side_zero_cross_moment
    assert_equal 0,Rithm210LatentShock.moments(n_a:0,n_b:6,base:Rational(1,2),delta:Rational(3,40))[:cross]
  end
  def test_bounds
    assert_raises(ArgumentError){Rithm210LatentShock.moments(n_a:3,n_b:3,base:0.9,delta:0.2)}
  end
end
