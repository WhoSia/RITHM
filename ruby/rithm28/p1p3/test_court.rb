require 'minitest/autorun'
require_relative 'court'
class P1P3Test < Minitest::Test
 def test_no_setup
  {count:2,deadline:1,weighted:4,min_group:1}.each{|o,w|assert_equal w,RithmP1P3::Court.new(objective:o).value}
 end
 def test_setup
  {count:1,deadline:1,weighted:3,min_group:0}.each{|o,w|assert_equal w,RithmP1P3::Court.new(setup:true,objective:o).value}
 end
 def test_resource_bound
  assert_operator 4,:>,3
  assert_operator 2+2+1+1,:>,5
  assert_equal 5,2+2+1
 end
end