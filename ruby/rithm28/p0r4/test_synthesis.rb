require 'minitest/autorun'
require_relative 'synthesis'
class P0R4Test < Minitest::Test
 def test_winners
  {false=>[0.5,5.0/12],true=>[5.0/6,5.0/12]}.each do |delay,wants|
   r=synth(delay)
   assert_equal 264,r[:count]
   assert_equal 140,r[:safe_count]
   [:zero,:one].each_with_index do |key,i|
    got=r.fetch(key)
    assert_in_delta wants[i],got[:value],1e-9
    assert got[:safe]
    refute got[:overflow]
   end
  end
 end
 def test_overflow
  [false,true].each{|delay|q=RithmQueue.new(p0(0),delay);assert q.unsafe;assert q.overflow}
 end
end
