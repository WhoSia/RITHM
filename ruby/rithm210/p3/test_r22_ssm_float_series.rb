require 'minitest/autorun'
require_relative 'r22_ssm_exact_series'
require_relative 'r22_ssm_float_series'
class TestRithm210R22SSMFloatSeries < Minitest::Test
  EXACT=Rithm210R22SSMExactSeries
  FAST=Rithm210R22SSMFloatSeries
  def test_random_histories_all_q
    rng=Random.new(20261106)
    80.times do
      a=Array.new(rng.rand(1..5)){rng.rand(-8..8)}
      b=Array.new(rng.rand(1..5)){rng.rand(-8..8)}
      [{paired_differences:a},{payoffs_a:a,payoffs_b:b}].each_with_index do |history,i|
        x=EXACT.probabilities(history:history,informed:i==0)
        y=FAST.probabilities(history:history,informed:i==0)
        9.times{|q|assert_in_delta x[q].to_f,y[q],1e-11}
      end
    end
  end
  def test_empty_sources
    assert_equal Array.new(9,0.5),FAST.probabilities(history:{payoffs_a:[],payoffs_b:[1]},informed:false)
    assert_equal Array.new(9,0.5),FAST.probabilities(history:{paired_differences:[]},informed:true)
  end
end
