require 'minitest/autorun'
require_relative 'ssm_generative'
class TestRithm210SSMTable7Replication < Minitest::Test
  REFERENCE={
    'ssm5_1'=>[[4.66,0.34],[4.29,0.18],[3.96,0.38],[4.17,0.35]],
    'ssm5_2'=>[[4.61,0.32],[4.35,0.21],[4.09,0.21],[4.15,0.25]],
    'ssm5_3'=>[[4.87,0.58],[4.49,0.35],[4.04,0.14],[4.11,0.25]],
    'ssm1_9_1'=>[[4.67,0.34],[4.33,0.19],[3.95,0.38],[4.15,0.35]],
    'ssm1_9_2'=>[[4.61,0.31],[4.37,0.22],[4.03,0.22],[4.10,0.26]],
    'ssm1_9_3'=>[[4.82,0.55],[4.46,0.34],[4.00,0.14],[4.08,0.25]]
  }.freeze
  def test_original_author_table7_simulated_means_and_standard_deviations
    result=Rithm210GenerativeSSM.run(replicates:10_000,seed:20261104)[:results]
    keys=[:cost_early,:cost_late,:a_early,:a_late]
    REFERENCE.each do |name,original|
      original.each_with_index do |(mu,sd),i|
        actual=result.fetch(name).fetch(keys.fetch(i))
        assert_in_delta mu,actual[:mean],0.03,"#{name} #{keys[i]} mean"
        assert_in_delta sd,actual[:sd],0.03,"#{name} #{keys[i]} sd"
      end
    end
  end
end
