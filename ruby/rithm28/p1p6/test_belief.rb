require 'minitest/autorun'
require_relative 'belief'
class P1P6Test < Minitest::Test
 EXPECT={5=>{1=>1,2=>1,3=>1,4=>1,100=>2},6=>{1=>0,2=>0,3=>0,4=>0,100=>1}}
 def test_information_age_bounds
  EXPECT.each{|h,ages|ages.each{|lag,want|(0..2).each{|b|
   assert_equal(b>=want,RithmP1P6::Solver.new(horizon:h,budget:b,lag:lag).solve)
  }}}
 end
 def test_initial_action_cannot_leak_hidden_shock
  [1,2,3,4,100].each{|lag|
   x=RithmP1P6::Solver.new(horizon:5,budget:2,lag:lag)
   assert x.solve
   assert x.witness.key?([0,(0..5).map{|i|[i,0,0]},2,0,0])
  }
 end
 def test_blind_baseline
  refute RithmP1P6::Solver.new(horizon:5,budget:1,lag:100).solve
  assert RithmP1P6::Solver.new(horizon:5,budget:2,lag:100).solve
 end
end