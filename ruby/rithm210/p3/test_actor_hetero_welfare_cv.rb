require 'minitest/autorun'
require_relative 'actor_hetero_welfare_cv'
class TestRithm210ActorHeteroWelfareCV < Minitest::Test
  M=Rithm210ActorHeteroWelfareCV
  def fake_people
    [1,1,1,1,0,0].each_with_index.map do |a,i|
      {'RouteA'=>a.to_s,'switchAtoBWill'=>'0','switchBtoAWill'=>'0',
       'NumAnext'=>'4'}
    end
  end
  def test_heterogeneous_probs_predict_analytical_joint_and_loss
    p=[0.8,0,0,0,0.8,0]
    m=M.predict(fake_people,p)
    assert_in_delta 1.6,m[:gross],1e-12
    assert_in_delta 0.04,m[:zero],1e-12
    assert_in_delta 0.64,m[:cancel],1e-12
    assert_in_delta 0.96,m[:loss],1e-12
  end
  def test_observed_unchanged_group
    m=M.observed(fake_people)
    assert_equal 1,m[:zero]
    assert_equal 0,m[:cancel]
    assert_equal 0,m[:gross]
    assert_equal 0,m[:loss]
  end
  def test_summary_is_observed_minus_prediction
    rows=[{session:1,model: :baseline,epoch: :early,
      observed:{zero:1,cancel:0,gross:0,loss:0},
      predicted:{zero:0.2,cancel:0.1,gross:1,loss:3}}]
    r=M.summary(rows)
    assert_equal 1,r[:n]
    assert_in_delta 0.8,r[:residual][:zero],1e-12
    assert_in_delta(-0.1,r[:residual][:cancel],1e-12)
    assert_in_delta(-1,r[:residual][:gross],1e-12)
    assert_in_delta(-3,r[:residual][:loss],1e-12)
    assert_raises(RuntimeError){M.summary([])}
  end
end
