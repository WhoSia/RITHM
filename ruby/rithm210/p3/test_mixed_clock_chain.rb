require 'minitest/autorun'
require_relative 'mixed_clock_chain'
require_relative 'shock_afterlife'
class TestMixedClockChain < Minitest::Test
 M=Rithm210MixedClockChain
 def test_stochastic_matrix
  [0,Rational(1,2),Rational(9,10),1].each do |s|
   (0..6).each do |n|
    assert_equal 1,M.transition(n,sync:s).values.sum
    assert_equal({4=>1},M.transition(n,sync:s).to_h) if n==4
   end
  end
 end
 def test_pure_async_agrees_with_previous_formula
  x=M.expected_hitting_times(sync:0)
  assert_equal Rational(57,10),x[0]
  assert_equal Rational(11,5),x[6]
  assert_equal 2,x[3]
  assert_equal Rational(6,5),x[5]
  [3,5].each do |n|
   assert_equal Rithm210ShockAfterlife.discounted_async_random_actor(
     post_shock_n:n,beta:Rational(9,10)),M.discounted_excess(
       sync:0,discount:Rational(9,10))[n]
  end
 end
 def test_pure_sync_matches_previous_formula
  x=M.discounted_excess(sync:1,discount:Rational(9,10))
  [3,5].each do |n|
   assert_equal Rithm210ShockAfterlife.discounted_sync(
     post_shock_n:n,beta:Rational(9,10)),x[n]
  end
  assert_raises(ArgumentError){M.expected_hitting_times(sync:1)}
 end
 def test_midpoint_hitting_times_are_exact
  x=M.expected_hitting_times(sync:Rational(1,2))
  assert_equal Rational(66,7),x[3]
  assert_equal Rational(60,7),x[5]
 end
 def test_inverse_square_small_async_probability
  [Rational(9,10),Rational(99,100),Rational(999,1000)].each do |s|
   t=M.expected_hitting_times(sync:s)[3]
   normalized=(1-s)**2*t
   assert_in_delta Rational(12,5).to_f,normalized.to_f,0.15
  end
 end
 def test_finite_horizon_probability_and_loss
  rows=M.finite_horizon(sync:Rational(1,2),start:3,horizon:30)
  assert_equal 30,rows.length
  assert_equal 0,rows.first[:prob_optimum]
  assert_equal 3,rows.first[:expected_excess]
  assert_operator rows.last[:prob_optimum],:>,0
  assert_operator rows.last[:prob_optimum],:<,1
 end
end
