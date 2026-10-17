require 'minitest/autorun'
require_relative 'audit'
class AuditTest < Minitest::Test
 def test_equivalence_vs_provenance
  r=RithmP1P10.report
  assert_equal 6,r['worlds']
  assert r['published_shift_observation_equivalent']
  assert r['published_shift_distinct_digest']
  refute r['earlier_receipt_observation_equivalent']
 end
 def test_no_prepublished_event
  a=RithmP1P10.evidence(5);a[0]['published']=0
  assert_raises(RuntimeError){RithmP1P10.validate!(a,5)}
  a=RithmP1P10.evidence(5);a[0]['received']=0
  assert_raises(RuntimeError){RithmP1P10.validate!(a,5)}
 end
 def test_no_future_input
  a=RithmP1P10.evidence(5);w=[1,0,0,0,0]
  assert_empty RithmP1P10.observation(a,0,w)
  assert_empty RithmP1P10.observation(a,3,w)
  assert_equal [[0,1]],RithmP1P10.observation(a,4,w)
 end
end