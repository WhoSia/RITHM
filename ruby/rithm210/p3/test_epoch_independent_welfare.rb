require 'minitest/autorun'
require_relative 'epoch_independent_welfare'
class TestRithm210EpochIndependentWelfare < Minitest::Test
  M=Rithm210EpochIndependentWelfare
  def actor(y)
    {'trt'=>'3','Informed'=>'1','RouteA'=>'1','Cost'=>'4.0','switchWill'=>y.to_s}
  end
  def test_epoch_cutoffs
    assert_equal :early,M.epoch(1)
    assert_equal :early,M.epoch(10)
    assert_equal :middle,M.epoch(11)
    assert_equal :middle,M.epoch(29)
    assert_equal :late,M.epoch(30)
  end
  def test_training_fold_exclusion
    g={[1,1,1,1]=>[actor(1)],[1,1,1,30]=>[actor(0)],[2,1,1,1]=>[actor(0)]}
    k=[*Rithm210OnlineIdentity.actor_key(actor(1)),:early]
    t=M.train_epoch(g,[2])
    assert_equal [1,1],t.fetch(k)
    assert_in_delta(1+20*0.2,21*M.probability(0.2,t,actor(0),1),1e-12)
    t2=M.train_epoch(g,[1])
    assert_equal [0,1],t2.fetch(k)
    assert_in_delta 0.2,M.probability(0.2,t,actor(0),17),1e-12
  end
  def test_unseen_stratum_uses_base_and_invalid_alpha_rejected
    t=M.train_epoch({},[])
    assert_in_delta 0.3,M.probability(0.3,t,actor(0),1),1e-12
    assert_raises(ArgumentError){M.probability(0.3,t,actor(0),1,alpha:0)}
  end
end
