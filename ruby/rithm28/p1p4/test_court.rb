require 'minitest/autorun'
require_relative 'court'
class P1P4Test < Minitest::Test
 EXPECT={none:[2,1,1,1,4],learn_once:[1,1,1,0,3],always:[1,1,1,0,3]}
 def test_complete_minimax
  EXPECT.each{|m,a|[:count,:a,:b,:both,:weighted].each_with_index{|g,i|
   assert_equal a[i],RithmP1P4::Court.new(mode:m,goal:g).solve
  }}
 end
 def test_budget_threshold
  assert_equal 0,RithmP1P4::Court.new(mode: :learn_once,goal: :both).solve
  assert_equal 1,RithmP1P4::Court.new(mode: :learn_once,goal: :both,horizon:6).solve
 end
 def test_independent_go_consistency_contract
  assert_equal 1,RithmP1P4::Court.new(mode: :always,goal: :a).solve
  assert_equal 1,RithmP1P4::Court.new(mode: :always,goal: :b).solve
  assert_equal 0,RithmP1P4::Court.new(mode: :always,goal: :both).solve
 end
end