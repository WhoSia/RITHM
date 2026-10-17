require 'minitest/autorun'
require_relative 'receipt'
class P1P7Test < Minitest::Test
 EXPECT={5=>{lag1:1,lag4:1,reorder:1,late:1,blackout:2},6=>{lag1:0,lag4:0,reorder:0,late:0,blackout:1}}
 def test_synth_and_replay
  EXPECT.each{|h,patterns|patterns.each{|p,want|
   c=RithmP1P7::Contract.new(h:h,pattern:p)
   (0..2).each{|b|assert_equal(b>=want,RithmP1P7::Solver.new(h:h,budget:b,contract:c).solve)}
   assert_operator RithmP1P7::Solver.new(h:h,budget:want,contract:c).replay!,:>,0
  }}
 end
 def test_uncertified
  [5,6].each{|h|
   c=RithmP1P7::Contract.new(h:h,pattern: :lag1,certified:false)
   want=h==5 ? 2 : 1
   assert_equal want,(0..2).find{|b|RithmP1P7::Solver.new(h:h,budget:b,contract:c).solve}
  }
 end
 def test_out_of_order
  c=RithmP1P7::Contract.new(h:5,pattern: :reorder)
  assert_equal [[1,1]],c.observation(2,[0,1,0,0,0])
  assert_empty c.observation(1,[1,0,0,0,0])
  assert_equal [[0,1],[2,0]],c.observation(4,[1,0,0,0,0])
 end
 def test_clocks
  c=RithmP1P7::Contract.new(h:5,pattern: :reorder)
  c.events.each{|e|assert_operator e.received,:>=,e.published;assert_operator e.published,:>,e.event}
  c.events.first.received=0
  assert_raises(RuntimeError){c.validate!}
 end
end