require 'minitest/autorun'
require_relative 'nested_online_actor_cv'

class TestRithm210NestedOnlineHistory < Minitest::Test
  N=Rithm210NestedOnlineHistory

  def test_session_fold_balance
    m=N.folds((1..24).to_a,6)
    assert_equal 24,m.size
    assert_equal [4,4,4,4,4,4],(0...6).map{|f|m.values.count(f)}
  end

  def test_online_model_uses_prior_outcomes_only
    # Same actor. At t=1 there is no observed individual switch history.
    actor=->(period,sw){{
      'trt'=>'1','Informed'=>'0','RouteA'=>'0','Cost'=>'4',
      'ID'=>'1','switchWill'=>sw.to_s,'switchBtoAWill'=>sw.to_s,
      'switchAtoBWill'=>'0'}}
    # Single-person toy group: evaluate only, not the full-source group validation.
    source={
      [1,2,1,1]=>[actor.call(1,0)],
      [1,2,1,2]=>[actor.call(2,1)]
    }
    result=N.evaluate(source,[],[1],strengths:[20.0])
    assert_equal 2,result[:baseline][:n]
    assert_equal 2,result[:within_section_20][:n]
    # Training-free baseline prior is 0.5 for both t=1,t=2.
    assert_in_delta 0.5,Rithm210OnlineIdentity.probability(
      Rithm210OnlineIdentity.train(source,[1]),actor.call(1,0)),1e-12
    assert_operator result[:within_section_20][:joint],:>,0
  end

  def test_inner_fold_disjointness
    sessions=(1..24).to_a
    outer=N.folds(sessions,6)
    test=sessions.select{|s|outer[s]==0}
    training=sessions-test
    inner=N.folds(training,5)
    assert_equal 4,test.size
    assert_equal 20,training.size
    (0...5).each do |f|
      val=training.select{|s|inner[s]==f}
      fit=training-val
      assert_equal 4,val.size
      assert_equal 16,fit.size
      assert_empty fit & test
      assert_empty fit & val
    end
  end
end
