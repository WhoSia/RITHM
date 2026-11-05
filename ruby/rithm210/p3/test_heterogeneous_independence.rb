require 'minitest/autorun'
require_relative 'heterogeneous_independence'
class TestRithm210HeterogeneousIndependence < Minitest::Test
  M=Rithm210HeterogeneousIndependence
  def test_homogeneous_exact_special_case
    [0.0,0.1,0.5,1.0].each do |e|
      x=M.analyze(Array.new(6,e))
      assert_in_delta 6*e,x[:gross],1e-12
      assert_in_delta (1-e)**6,x[:zero],1e-12
      assert_in_delta 18*e-6*e*e,x[:next_excess],1e-10
    end
  end
  def test_independence_does_not_imply_homogeneous_welfare
    # One sure A-to-B and one sure B-to-A mover: independent but fully offset.
    x=M.analyze([1.0,0,0,0,1.0,0])
    assert_equal 2.0,x[:gross]
    assert_equal 0.0,x[:next_excess]
    assert_equal 1.0,x[:cancellation]
    # Compare six i.i.d. Bernoulli actors with SAME expected gross.
    y=M.analyze(Array.new(6,Rational(1,3).to_f))
    assert_in_delta 2.0,y[:gross],1e-12
    assert_operator y[:next_excess],:>,5
  end
  def test_nontrivial_stochastic_heterogeneity
    x=M.analyze([0.8,0,0,0,0.8,0])
    assert_in_delta 1.6,x[:gross],1e-12
    assert_in_delta 0.96,x[:next_excess],1e-12
    assert_in_delta 0.64,x[:cancellation],1e-12
    assert_in_delta 0.04,x[:zero],1e-12
  end
  def test_invalid_probabilities
    assert_raises(ArgumentError){M.analyze([0.1]*5)}
    assert_raises(ArgumentError){M.analyze([1.1]+[0]*5)}
  end
end
