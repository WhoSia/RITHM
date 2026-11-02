require 'minitest/autorun'
require_relative 'actor_markov_joint'
class ActorMarkovJointTest < Minitest::Test
 def test_empty
  assert_equal [1.0],RithmActorMarkov.convolve([])
 end
 def test_two_independent_switchers
  p=RithmActorMarkov.convolve([0.2,0.3])
  assert_in_delta 0.56,p[0]
  assert_in_delta 0.38,p[1]
  assert_in_delta 0.06,p[2]
  assert_in_delta 1.0,p.sum
 end
 def test_finite_probability
  p=RithmActorMarkov.convolve([0.1,0.7,0.4])
  assert p.all?{|x| x.finite? && x>=0}
  assert_in_delta 1.0,p.sum
 end
end
