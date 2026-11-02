require 'minitest/autorun'
require_relative 'residual_independence_audit'
class RithmResidualAuditTest < Minitest::Test
 def test_zero_at_calibrated_counts
  assert_in_delta 0.0,RithmResidualAudit.cross_residual(2,1,2.0,1.0),1e-12
 end
 def test_residual_sign
  assert_in_delta 0.25,RithmResidualAudit.cross_residual(2,2,1.5,1.5),1e-12
  assert_in_delta -0.25,RithmResidualAudit.cross_residual(2,1,1.5,1.5),1e-12
 end
 def test_convolution_mass
  assert_in_delta 1.0,RithmActorMarkov.binomial_convolution([0.1,0.2,0.7]).sum,1e-12
 end
end
