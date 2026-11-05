require 'minitest/autorun'
require_relative 'finite_horizon_independent_welfare'
class TestRithm210FiniteHorizonIndependentWelfare < Minitest::Test
  M=Rithm210FiniteHorizonIndependentWelfare
  def test_binomial_mass_and_extreme_probabilities
    (0..6).each do |n|
      [0.to_r,Rational(1,4),Rational(2,3),1.to_r].each do |p|
        assert_equal 1,(0..n).sum{|k|M.binomial(n,k,p)}
      end
    end
    assert_equal 1,M.binomial(2,0,0)
    assert_equal 1,M.binomial(2,2,1)
    assert_equal 0,M.binomial(2,1,0)
  end
  def test_kernel_stochastic_and_deterministic_extremes
    k=M.kernel(a:0,b:0)
    (0..6).each{|i|assert_equal 1,k[i][i];assert_equal 1,k[i].sum}
    k=M.kernel(a:1,b:1)
    (0..6).each{|i|assert_equal 1,k[i][6-i]}
  end
  def test_one_step_same_mean_but_different_variance
    slow=M.run(a:Rational(1,10),b:Rational(1,5),horizon:2)
    fast=M.run(a:Rational(1,4),b:Rational(1,2),horizon:2)
    s=slow[:path][1];f=fast[:path][1]
    assert_equal 4,s[:mean]
    assert_equal 4,f[:mean]
    assert_equal Rational(17,25),s[:variance]
    assert_equal Rational(5,4),f[:variance]
    assert_equal Rational(51,25),s[:excess]
    assert_equal Rational(15,4),f[:excess]
    assert_operator fast[:cumulative_discounted_excess],:>,slow[:cumulative_discounted_excess]
  end
  def test_same_stationary_distribution_but_distinct_finite_horizon
    r=M.same_stationary_mean_comparison(horizon:40)
    assert_operator r[:difference],:>,0
    assert_in_delta 3.5764705882,r[:difference].to_f,1e-8
    [Rational(1,10),Rational(1,4)].each do |a|
      k=M.kernel(a:a,b:2*a)
      pi=(0..6).map{|n|M.binomial(6,n,Rational(2,3))}
      assert_equal pi,M.next_distribution(pi,k)
      assert_equal 4,M.expected_excess(pi)
    end
  end
  def test_invalid_inputs
    assert_raises(ArgumentError){M.kernel(a:-0.1,b:0.1)}
    assert_raises(ArgumentError){M.kernel(a:0.1,b:2)}
    assert_raises(ArgumentError){M.run(a:0,b:0,start:7)}
    assert_raises(ArgumentError){M.run(a:0,b:0,horizon:0)}
    assert_raises(ArgumentError){M.run(a:0,b:0,discount:1.1)}
  end
end
