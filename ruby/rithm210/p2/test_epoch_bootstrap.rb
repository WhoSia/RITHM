require 'minitest/autorun'
require_relative 'epoch_bootstrap'
class TestEpochBootstrap < Minitest::Test
  Q=Rithm210EpochBootstrap
  def test_zero_difference
    rows=[{session:1,n:117,joint:0.0,count:0.0,cross:0.0},
          {session:2,n:351,joint:0.0,count:0.0,cross:0.0}]
    r=Q.run(rows,draws:100)
    [:joint,:count,:cross].each do |head|
      assert_equal 0.0,r[head][:mean]
      assert_equal 0.0,r[head][:lower]
      assert_equal 0.0,r[head][:upper]
    end
  end
  def test_weighted_mean_and_repeatability
    rows=[{session:1,n:1,joint:-1.0,count:-1.0,cross:-1.0},
          {session:2,n:3,joint:1.0,count:1.0,cross:1.0}]
    x=Q.run(rows,draws:100)
    assert_in_delta 0.5,x[:joint][:mean],1e-12
    assert_equal x,Q.run(rows,draws:100)
  end
end
