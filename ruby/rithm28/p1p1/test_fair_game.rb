require 'minitest/autorun'
require_relative 'fair_game'
class FairGameTest < Minitest::Test
 def setup;@g=RithmP1P1::Game.new;end
 def test_reachable
  assert_equal 4,@g.reachable.size
  assert_includes @g.reachable,:restored
 end
 def test_weak_allows_intermittent_starvation
  assert @g.fair_nonrestored(:weak).any?{|x|x[:states]==[:off,:on]}
  refute @g.fair_nonrestored(:weak).any?{|x|x[:states]==[:ordered]}
 end
 def test_strong_prevents_starvation
  assert_empty @g.fair_nonrestored(:strong)
 end
 def test_person_label
  c=@g.identity_counterexample
  assert c[:same_counts]
  assert_equal [true,false],c[:pending_b2]
 end
end