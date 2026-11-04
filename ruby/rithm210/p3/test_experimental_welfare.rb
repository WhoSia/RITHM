require 'minitest/autorun'
require_relative 'experimental_welfare'
class TestRithm210ExperimentalWelfare < Minitest::Test
  M=Rithm210ExperimentalWelfare
  def test_exact_6_person_cost_for_every_occupancy
    assert_equal [72,51,36,27,24,27,36],(0..6).map{|n|M.cost(n)}
    (0..6).each{|n|assert_equal 3*(n-4)**2,M.excess(n)}
  end
  def test_coupling_changes_welfare_at_identical_switch_means
    a=M.coupling_examples
    assert_equal [0,Rational(3,2),3],[:positive,:independent,:negative].map{|k|a[k][:expected_excess]}
    assert_equal [4,4,4],[:positive,:independent,:negative].map{|k|a[k][:mean_next_a]}
    assert_equal [Rational(1,4),0,Rational(-1,4)],
      [:positive,:independent,:negative].map{|k|a[k][:covariance_up_down]}
  end
  def test_direct_expected_cost_and_moment_identity
    q=M.expected_excess(current_a:3,joint:{
      [0,0]=>Rational(1,2),[1,0]=>Rational(1,2)})
    assert_equal Rational(3,2),q[:expected_excess]
    assert_equal q[:expected_excess],q[:identity_value]
  end
  def test_reject_out_of_support_and_bad_mass
    assert_raises(ArgumentError){M.cost(7)}
    assert_raises(ArgumentError){M.expected_excess(current_a:4,joint:{[3,0]=>1})}
    assert_raises(ArgumentError){M.expected_excess(current_a:4,joint:{[0,0]=>0.9})}
  end
end
