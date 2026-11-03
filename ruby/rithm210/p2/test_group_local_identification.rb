require 'minitest/autorun'
require_relative 'group_local_identification'
class TestGroupLocalIdentification < Minitest::Test
  M=Rithm210GroupLocalIdentification
  def test_exact_group_observational_equivalence
    (0..6).each do |a|
      opts={a:a,p:Rational(1,2),delta:Rational(3,40)}
      assert_equal M.group_law(**opts),M.directed_law(**opts)
      assert_equal Rational(1),M.group_law(**opts).values.sum
    end
  end
  def test_full_two_group_distribution_normalizes
    law=M.two_group_law(a:3,p:Rational(1,2),delta:Rational(3,40))
    assert_equal Rational(1),law.values.sum
    assert_equal 256,law.size
  end
  def test_distinguish_group_local_from_session_global_using_cross_group_moment
    m=M.predicted_moments(a:3,p:Rational(1,2),delta:Rational(3,40))
    assert_equal Rational(81,1600),m[:within]
    assert_equal 0,m[:between]
  end
  def test_intervention_inequivalence
    o={a:3,p:Rational(1,2),delta:Rational(3,40)}
    assert_equal Rational(3,2),M.latent_do_d_mean(**o,u:0)
    assert_equal Rational(3,2),M.latent_do_d_mean(**o,u:3)
    assert_operator M.directed_do_d_mean(**o,u:0),:<,Rational(3,2)
    assert_operator M.directed_do_d_mean(**o,u:3),:>,Rational(3,2)
  end
  def test_delta_zero
    o={a:3,p:Rational(1,2),delta:0}
    assert_equal 0,M.predicted_moments(**o)[:within]
    assert_equal Rational(3,2),M.directed_do_d_mean(**o,u:0)
  end
end
