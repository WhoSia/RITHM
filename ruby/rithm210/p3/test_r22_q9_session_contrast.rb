require 'minitest/autorun'
require_relative 'r22_q9_session_contrast'
class TestRithm210R22Q9SessionContrast < Minitest::Test
  M=Rithm210R22Q9SessionContrast
  def fixture
    (1..4).flat_map do |s|
      %w[persistent_q9 persistent_q3 frequency].map do |name|
        offset={'persistent_q9'=>2.0,'persistent_q3'=>1.0,'frequency'=>0.0}.fetch(name)
        {session:s,treatment:3,model:name,groups:40,logloss:s/10.0+offset,
         brier:s/50.0+offset,cost_abs_error:s+offset}
      end
    end
  end
  def test_paired_exact_sign_and_deterministic_sampling
    a=M.compare(fixture,treatment:3,candidate:'persistent_q9',baseline:'persistent_q3',draws:300,seed:7)
    assert_equal a,M.compare(fixture,treatment:3,candidate:'persistent_q9',baseline:'persistent_q3',draws:300,seed:7)
    assert_equal 4,a[:sessions]
    assert_in_delta 1.0,a[:metrics][:logloss][:mean_difference],1e-12
    assert_equal [1.0,1.0],a[:metrics][:cost_abs_error][:percentile95]
    assert_equal 0,a[:metrics][:brier][:candidate_better_sessions]
  end
  def test_unpaired_or_duplicate_session_rejected
    a=fixture.reject{|r|r[:session]==4 && r[:model]=='frequency'}
    assert_raises(ArgumentError){M.compare(a,treatment:3,candidate:'persistent_q9',baseline:'frequency')}
    a=fixture+[fixture.first]
    assert_raises(ArgumentError){M.compare(a,treatment:3,candidate:'persistent_q9',baseline:'frequency')}
  end
  def test_unmatched_group_count_rejected
    a=fixture;a.first[:groups]=80
    assert_raises(ArgumentError){M.compare(a,treatment:3,candidate:'persistent_q9',baseline:'persistent_q3')}
  end
end
