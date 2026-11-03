require 'minitest/autorun'
require_relative 'residual_negative_control'
class TestRithm210ResidualNegativeControl < Minitest::Test
  Q=Rithm210ResidualNegativeControl
  def test_key_uses_own_history
    r={'trt'=>'2','Informed'=>'1','RouteA'=>'0','Cost'=>'5'}
    assert_equal [2,1,0,5.0],Q.key(r)
  end
  def test_smoothed_training_count
    row={'trt'=>'1','Informed'=>'0','RouteA'=>'1','Cost'=>'5','switchWill'=>'1'}
    group={ [3,1,1,1]=>[row] }
    m=Q.fit(group,{3=>0},1)
    assert_in_delta (1+20*(2.0/3))/(1+20),Q.probability(m,row),1e-12
  end
  def test_exclusion_of_heldout_fold
    row={'trt'=>'1','Informed'=>'0','RouteA'=>'1','Cost'=>'5','switchWill'=>'1'}
    group={ [3,1,1,1]=>[row] }
    m=Q.fit(group,{3=>0},0)
    assert_in_delta 0.5,Q.probability(m,row),1e-12
  end
  def test_paired_bootstrap_zero
    rows=[{session:1,x:0.0},{session:2,x:0.0}]
    b=Q.bootstrap(rows,:x,draws:100)
    assert_equal 0,b[:mean]
    assert_equal 0,b[:lower]
    assert_equal 0,b[:upper]
  end
  def test_bootstrap_repeatability
    rows=[{session:1,x:1.0},{session:2,x:-1.0},{session:3,x:0.0}]
    assert_equal Q.bootstrap(rows,:x,draws:100),Q.bootstrap(rows,:x,draws:100)
  end
end
