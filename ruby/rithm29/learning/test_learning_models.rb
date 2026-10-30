require 'minitest/autorun'
require_relative 'learning_models'
class LearningModelsTest < Minitest::Test
  def test_belief
    assert_equal [0,1,2,3,4,5],RithmLearningModels.compatible_other_counts(route_a:1,payoff:5)
    assert_in_delta 1,RithmLearningModels.belief(route_a:1,payoff:5).sum
    assert_equal [5],RithmLearningModels.compatible_other_counts(route_a:1,payoff:0)
    assert_in_delta 1.5,RithmLearningModels.inferred_counterfactual(route_a:1,payoff:5)
  end
  def test_counterfactual
    assert_equal 3.0,RithmLearningModels.informed_counterfactual(route_a:1,payoff:5,total_a:4)
  end
  def test_hidden_fields_ignored
    a=RithmLearningModels::EWA.new(informed:false)
    b=RithmLearningModels::EWA.new(informed:false)
    assert_equal a.update(route_a:1,payoff:5),b.update(route_a:1,payoff:5,total_a:6)
    assert_equal a.attractions,b.attractions
  end
  def test_ewa_initial
    e=RithmLearningModels::EWA.new(informed:false,lambda:2)
    assert_in_delta 0.5,e.probability_a
    x=e.update(route_a:1,payoff:5)
    assert_in_delta 1,x[:phi]
    assert_in_delta 2,e.n
    assert_in_delta 2.5,x[:expected_others_a]
  end
  def test_ssm_uninformed
    s=RithmLearningModels::SmallSample.new(informed:false,rng:Random.new(1))
    s.observe(route_a:1,payoff:8)
    assert_includes [0,1],s.choose
    s.observe(route_a:0,payoff:3)
    10.times { assert_equal 1,s.choose }
  end
  def test_ssm_informed
    s=RithmLearningModels::SmallSample.new(informed:true,rng:Random.new(1))
    s.observe(route_a:1,payoff:5,total_a:4)
    assert_equal 1,s.choose
  end
end
