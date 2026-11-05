require 'minitest/autorun'
require_relative 'r18_preanalysis_manifest'
class TestRithm210R18PreanalysisManifest < Minitest::Test
  M=Rithm210R18PreanalysisManifest
  def test_distinct_estimands
    a=M.draft(design: :two_condition)
    b=M.draft(design: :four_condition)
    assert_equal 2,a[:conditions].size
    assert_equal 4,b[:conditions].size
    refute_equal a[:estimand],b[:estimand]
    refute_equal M.fingerprint(a),M.fingerprint(b)
  end
  def test_stable_canonical_fingerprint
    a=M.draft
    b=a.to_a.reverse.to_h
    assert_equal M.fingerprint(a),M.fingerprint(b)
    b[:horizon]=39
    assert_raises(ArgumentError){M.fingerprint(b)}
  end
  def test_reject_after_allocation_baseline_or_new_primary
    a=M.draft;a[:baseline]='after_assignment_occupancy'
    assert_raises(ArgumentError){M.fingerprint(a)}
    b=M.draft;b[:primary]='switch_rate_selected_posthoc'
    assert_raises(ArgumentError){M.fingerprint(b)}
  end
  def test_draft_status
    assert_equal 'unregistered_method_draft',M.draft[:status]
    assert_equal 40,M.draft[:horizon]
  end
end
