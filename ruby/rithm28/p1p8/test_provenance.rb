require 'minitest/autorun'
require_relative 'provenance'
class P1P8Test < Minitest::Test
 def test_all_cells
  {5=>{clean:1,duplicate:1,missing:1,untrusted:2,mislabel:1,reorder:1},6=>{clean:0,duplicate:0,missing:0,untrusted:1,mislabel:0,reorder:0}}.each{|h,cases|
   cases.each{|kind,value|assert_equal value,RithmP1P8.minimum(h:h,kind:kind)}
  }
 end
 def test_idempotence
  a=RithmP1P8::Contract.new(h:5,kind: :clean)
  b=RithmP1P8::Contract.new(h:5,kind: :duplicate)
  0.upto(5){|t|assert_equal a.observation(t,[1,0,0,0,0]),b.observation(t,[1,0,0,0,0])}
 end
 def test_conflict_rejection
  assert_raises(RuntimeError){RithmP1P8::Contract.new(h:5,kind: :conflict)}
 end
 def test_untrusted_and_mislabeled
  c=RithmP1P8::Contract.new(h:5,kind: :untrusted)
  0.upto(5){|t|assert_empty c.observation(t,[1,0,0,0,0])}
  d=RithmP1P8::Contract.new(h:5,kind: :mislabel)
  assert_empty d.observation(1,[1,0,0,0,0])
 end
end