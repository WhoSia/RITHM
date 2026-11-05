require 'minitest/autorun'
require_relative 'r20_session_contrast'
class TestRithm210R20SessionContrast < Minitest::Test
  M=Rithm210R20SessionContrast
  def fixture
    (1..4).flat_map do |sid|
      [:ssm_persistent,:own_route_frequency].map do |model|
        base=model==:ssm_persistent ? 1.0 : 0.5
        {session:sid,treatment:3,model:model,groups:80,logloss:base+sid/100.0,
         brier:base/2,cost_abs_error:base*2,cost_bias:base*3}
      end
    end
  end
  def test_paired_mean_and_seed_stability
    a=M.compare(fixture,treatment:3,model: :ssm_persistent,draws:200,seed:9)
    assert_equal a,M.compare(fixture,treatment:3,model: :ssm_persistent,draws:200,seed:9)
    assert_equal 4,a[:sessions]
    assert_in_delta 0.5,a[:metrics][:logloss][:mean_difference],1e-12
    assert_equal 0,a[:metrics][:logloss][:sessions_model_better]
    assert_in_delta 1.5,a[:metrics][:cost_bias][:mean_difference],1e-12
  end
  def test_reject_unpaired_duplicate_and_wrong_support
    assert_raises(ArgumentError){M.compare(fixture.first(2),treatment:3,model: :ssm_persistent)}
    bad=fixture.reject{|r|r[:session]==4&&r[:model]==:own_route_frequency}
    assert_raises(ArgumentError){M.compare(bad,treatment:3,model: :ssm_persistent)}
    assert_raises(ArgumentError){M.compare(fixture+fixture.first(1),treatment:3,model: :ssm_persistent)}
    bad=fixture;bad[0][:groups]=79
    assert_raises(ArgumentError){M.compare(bad,treatment:3,model: :ssm_persistent)}
    assert_raises(ArgumentError){M.compare(fixture,treatment:3,model: :ssm_persistent,draws:0)}
  end
  def test_accept_string_labels_from_json
    s=fixture.map{|r|r.merge(model:r[:model].to_s)}
    x=M.compare(s,treatment:3,model: :ssm_persistent,draws:12)
    assert_equal 4,x[:sessions]
  end
end
