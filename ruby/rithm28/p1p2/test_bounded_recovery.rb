require 'minitest/autorun'
require_relative 'bounded_recovery'
class CourtTest < Minitest::Test
 def test_four
  [[0,0,3],[1,0,5],[2,1,8],[3,2,11]].each{|r,d,n|assert_equal n,BoundedRecovery.worst(r,d)}
 end
end
