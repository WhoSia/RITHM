require 'minitest/autorun'
require_relative 'r18_randomization_inference'
class TestRithm210R18RandomizationInference < Minitest::Test
  M=Rithm210R18RandomizationInference
  def test_all_24_four_arm_randomizations_and_exact_sharp_null
    ids=[1,2,3,4]
    a=ids.zip(M::ARMS).to_h
    y={1=>10.0,2=>11.0,3=>14.0,4=>18.0}
    assert_equal 24,M.balanced_assignments(ids).count
    r=M.fisher_sharp_null(a,y)
    assert_equal 'exact Fisher sharp-null',r[:method]
    assert_equal 24,r[:assignments]
    assert r[:p_two_sided].between?(0,1)
    assert_in_delta M.estimate(a,y)[:interaction],r[:observed],1e-12
  end
  def test_2520_exact_assignments_for_8_independent_clusters
    ids=(1..8).to_a
    assert_equal 2520,M.balanced_assignments(ids).count
    a=M.randomize_sessions(ids,seed:7)
    y=ids.to_h{|id|[id,id.to_f]}
    result=M.fisher_sharp_null(a,y)
    assert_equal 2520,result[:assignments]
    assert_equal 2,result[:per_arm]
    assert_operator M.neyman_variance(a,y),:>=,0
  end
  def test_constant_outcome_sharp_null_p_is_one
    ids=(1..24).to_a
    a=M.randomize_sessions(ids,seed:20261105)
    y=ids.to_h{|id|[id,12.0]}
    v=M.fisher_sharp_null(a,y,draws:500,seed:42)
    assert_equal 'Monte Carlo Fisher sharp-null, add-one',v[:method]
    assert_equal 1.0,v[:p_two_sided]
    assert_in_delta 0.0,M.neyman_variance(a,y),1e-12
  end
  def test_reproducible_assignment_and_p_value
    ids=(1..24).to_a
    a=M.randomize_sessions(ids,seed:4)
    y=ids.to_h{|id|[id,id*1.2]}
    assert_equal a,M.randomize_sessions(ids,seed:4)
    assert_equal M.fisher_sharp_null(a,y,draws:100,seed:2),
                 M.fisher_sharp_null(a,y,draws:100,seed:2)
  end
  def test_reject_imbalanced_missing_nonfinite_and_low_sample_variance
    a={1=>:lagged_frozen,2=>:lagged_feedback,3=>:current_frozen,4=>:current_feedback}
    y={1=>1.0,2=>2.0,3=>3.0,4=>4.0}
    assert_raises(ArgumentError){M.neyman_variance(a,y)}
    assert_raises(ArgumentError){M.estimate(a,y.merge(5=>1.0))}
    assert_raises(ArgumentError){M.estimate(a,y.merge(4=>Float::NAN))}
    assert_raises(ArgumentError){M.randomize_sessions([1,2,3])}
    assert_raises(ArgumentError){M.fisher_sharp_null(a,y,draws:0)}
  end
end
