require 'minitest/autorun'
require_relative 'ssm_activity'
class TestRithm210SSMActivityMoments < Minitest::Test
  def test_seeded_full_information_activity_directions
    results=Rithm210GenerativeSSMActivity.run(replicates:10_000,seed:20261104)[:results]
    %w[ssm5_3 ssm1_9_3].each do |name|
      early=results.fetch(name).fetch(:early)
      late=results.fetch(name).fetch(:late)
      assert_operator early[:no_switch_rate],:>,late[:no_switch_rate]
      assert_operator early[:mean_gross],:<,late[:mean_gross]
      assert_operator early[:cancellation_rate],:<,late[:cancellation_rate]
      assert_operator early[:next_loss],:<,late[:next_loss]
    end
  end
  def test_instrumentation_does_not_alter_generative_game
    klass=Rithm210GenerativeSSM
    %i[ssm5 ssm1_9].each do |model|
      base=klass.simulate_one(treatment:3,model:model,rng:Random.new(2911))
      traced=klass.simulate_one(treatment:3,model:model,rng:Random.new(2911),activity:true)
      assert_equal base,traced.reject{|key,_|key==:activity}
    end
  end
end
