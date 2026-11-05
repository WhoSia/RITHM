require 'minitest/autorun'
require_relative 'qi_model_a_paired_bootstrap'
class TestRithm210QiModelAPairedBootstrap < Minitest::Test
  M=Rithm210QiModelAPairedBootstrap
  def test_paired_resampling_preserves_full_sessions
    blocks={
      1=>[{epoch: :early,joint_delta:0.1,count_delta:0.2},
          {epoch: :late,joint_delta:-0.3,count_delta:0.0}],
      2=>[{epoch: :early,joint_delta:0.5,count_delta:0.1},
          {epoch: :late,joint_delta:0.7,count_delta:-0.2}]
    }
    result=M.bootstrap([1,2],blocks,draws:200,seed:2)
    assert_equal 4,result[:all][:n]
    assert_in_delta 0.25,result[:all][:qi_minus_epoch_joint_logloss],1e-12
    assert_in_delta 0.30,result[:early][:qi_minus_epoch_joint_logloss],1e-12
    assert_in_delta 0.20,result[:late][:qi_minus_epoch_joint_logloss],1e-12
    assert_equal 200,result[:all][:valid_draws]
  end
  def test_reproducible_seed
    x={1=>[{epoch: :early,joint_delta:1.0,count_delta:0.0},
            {epoch: :late,joint_delta:2.0,count_delta:0.0}]}
    assert_equal M.bootstrap([1],x,draws:20,seed:4),
                 M.bootstrap([1],x,draws:20,seed:4)
  end
  def test_reject_invalid_bootstrap
    assert_raises(ArgumentError){M.bootstrap([],{},draws:10)}
    assert_raises(ArgumentError){M.bootstrap([1],{},draws:0)}
    assert_raises(RuntimeError){M.bootstrap([1],{},draws:10)}
  end
end
