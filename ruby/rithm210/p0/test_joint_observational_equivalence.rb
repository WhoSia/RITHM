require 'minitest/autorun'
require_relative 'joint_observational_equivalence'
class TestJointEquivalence < Minitest::Test
  Q=Rithm210JointEquivalence
  def test_rational_exact_observational_equivalence
    (0..6).each do |a|
      args={a:a,p:Rational(1,2),delta:Rational(3,40)}
      joint=Q.joint(**args)
      assert_equal Rational(1),joint.values.sum
      assert_equal joint,Q.direct_chain(**args)
    end
  end
  def test_causal_difference_even_when_observations_equal
    args={a:3,p:Rational(1,2),delta:Rational(3,40)}
    assert_equal Rational(3,2),Q.do_d_mean_latent(**args,u:0)
    assert_equal Rational(3,2),Q.do_d_mean_latent(**args,u:3)
    low=Q.do_d_mean_direct(**args,u:0)
    high=Q.do_d_mean_direct(**args,u:3)
    assert_operator high,:>,low
    refute_equal low,Rational(3,2)
  end
  def test_zero_shock_collapses_intervention_difference
    args={a:3,p:Rational(1,2),delta:0}
    assert_equal Q.do_d_mean_latent(**args,u:0),Q.do_d_mean_direct(**args,u:0)
    assert_equal Q.do_d_mean_latent(**args,u:3),Q.do_d_mean_direct(**args,u:3)
  end
end
