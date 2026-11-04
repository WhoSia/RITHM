require 'minitest/autorun'
require_relative 'ssm_q_sensitivity'
class TestRithm210SSMSampleSizeSensitivity < Minitest::Test
  M=Rithm210GenerativeSSM
  Q=Rithm210SSMSampleSizeSensitivity
  def test_sample_size_validation
    assert_raises(ArgumentError){M.simulate_one(treatment:3,model: :ssm5,rng:Random.new(1),fixed_q:0)}
    assert_raises(ArgumentError){M.simulate_one(treatment:3,model: :ssm1_9,rng:Random.new(1),fixed_q:5)}
  end
  def test_parameterization_preserves_ssm5_reference
    a=M.simulate_one(treatment:3,model: :ssm5,rng:Random.new(28))
    b=M.simulate_one(treatment:3,model: :ssm5,rng:Random.new(28),fixed_q:5)
    assert_equal a,b
  end
  def test_small_grid_reproducible
    a=Q.run(q_values:[1,5,30],replicates:100,seed:17)
    assert_equal a,Q.run(q_values:[1,5,30],replicates:100,seed:17)
    assert_equal [1,5,30],a[:full_q_sensitivity].keys
  end
end
