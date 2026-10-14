require 'minitest/autorun'
require_relative 'administrative_court'
class RithmP0R7Test < Minitest::Test
 def test_episode_accounting
  [:fifo_a_tie,:priority_a,:priority_b,:alternate].product([0,1,2],[false,true]).each{|p,f,r|
   x=RithmP0R7.simulate(policy:p,friction:f,repair:r)
   [:A,:B].each{|g|assert_equal x[:arrivals][g],x[:served][g]+x[:dropped][g]+x[:pending][g]}
   assert_equal 8,x[:trace].length
  }
 end
 def test_priority_changes_distribution
  a=RithmP0R7.simulate(policy: :priority_a)
  b=RithmP0R7.simulate(policy: :priority_b)
  assert_equal({A:8,B:0},a[:served]);assert_equal({A:0,B:8},b[:served])
 end
 def test_setup_loss
  a=RithmP0R7.simulate(policy: :alternate,friction:0)
  b=RithmP0R7.simulate(policy: :alternate,friction:2)
  assert_equal 8,a[:served].values.sum
  assert_equal 1,b[:served].values.sum
 end
 def test_repairs_count_as_new_episodes
  x=RithmP0R7.simulate(policy: :alternate,repair:true)
  assert_operator x[:reattempts].values.sum,:>,0
 end
end
