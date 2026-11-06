require 'minitest/autorun'
require_relative 'r22_ssm_exact_series'
require_relative 'r19_ssm_exact'
class TestRithm210R22SSMExactSeries < Minitest::Test
  NEW=Rithm210R22SSMExactSeries
  OLD=Rithm210R19SSMExact
  def test_informed_all_nine_sample_sizes
    [[],[0],[-20,10,0],[-40,-10,20,30],[10,10,10,-20]].each do |pool|
      actual=NEW.probabilities(history:{paired_differences:pool},informed:true)
      assert_equal 9,actual.size
      (1..9).each{|q|assert_equal OLD.informed_probability(pool,q:q),actual[q-1]}
    end
  end
  def test_uninformed_all_nine_sample_sizes
    [[[],[]],[[10],[-10]],[[0,3],[-2,7]],[[8,8,5],[7,5,3]],[[20,-10,0],[-10,-10,4]]].each do |a,b|
      actual=NEW.probabilities(history:{payoffs_a:a,payoffs_b:b},informed:false)
      assert_equal 9,actual.size
      (1..9).each{|q|assert_equal OLD.uninformed_probability(a,b,q:q),actual[q-1]}
    end
  end
  def test_ties_and_symmetric_payoffs
    assert_equal Array.new(9,Rational(1,2)),NEW.series_from_pool([-4,-2,2,4],qmax:9)
    assert_equal Array.new(9,Rational(1,2)),NEW.probabilities(history:{payoffs_a:[],payoffs_b:[1]},informed:false)
  end
  def test_invalid_inputs
    assert_raises(ArgumentError){NEW.series_from_pool([])}
    assert_raises(ArgumentError){NEW.series_from_pool([1],qmax:10)}
    assert_raises(ArgumentError){NEW.series_from_pool([1.0])}
    assert_raises(ArgumentError){NEW.probabilities(history:{},informed:1)}
  end
end
