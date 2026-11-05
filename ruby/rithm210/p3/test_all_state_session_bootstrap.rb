require 'minitest/autorun'
require_relative 'all_state_session_bootstrap'
class TestRithm210AllStateSessionBootstrap < Minitest::Test
  M=Rithm210AllStateSessionBootstrap
  def record(trt,epoch,joint)
    {trt:trt,epoch:epoch,metrics:{joint:joint,count:joint/2.0,error:-joint,gross_pred:joint/4.0}}
  end
  def test_paired_session_blocks_and_stratum_coverage
    blocks={1=>[record(3,:early,-0.2),record(1,:middle,0.1)],
            2=>[record(3,:late,0.3),record(3,:early,-0.4)]}
    result=M.bootstrap([1,2],blocks,draws:200,seed:7)
    assert_equal 4,result[:all][:n]
    assert_in_delta -0.05,result[:all][:point][:joint],1e-12
    assert_equal 2,result[:full_early][:n]
    assert_in_delta -0.3,result[:full_early][:point][:joint],1e-12
    assert_equal 1,result[:full_late][:n]
    assert_equal [0.3,0.3],result[:full_late][:conditional_session_bootstrap95][:joint]
  end
  def test_seed_reproducibility
    blocks={1=>[record(3,:early,-0.2),record(3,:late,0.1)],
            2=>[record(3,:early,-0.4),record(3,:late,0.3)]}
    assert_equal M.bootstrap([1,2],blocks,draws:25,seed:14),
                 M.bootstrap([1,2],blocks,draws:25,seed:14)
  end
  def test_validation_and_empty_cells
    assert_raises(ArgumentError){M.quantile([],0.5)}
    assert_raises(ArgumentError){M.bootstrap([1],{},draws:0)}
    assert_raises(RuntimeError){M.bootstrap([1],{},draws:5)}
  end
end
