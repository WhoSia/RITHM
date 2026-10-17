require 'minitest/autorun'
require_relative 'monitor'
class TestP0R9 < Minitest::Test
 def test_recognized_authority_with_delivery
  e=[{event: :drop},{event: :appeal_file},{event: :repair_decision,body: :authorized},{event: :deliver,receipt:true}]
  assert_equal :restored,RithmR9.authority_trace(e)[:final]
 end
 def test_other_body_not_enough
  e=[{event: :drop},{event: :appeal_file},{event: :repair_decision,body: :other},{event: :deliver,receipt:true}]
  refute RithmR9.authority_trace(e)[:restored]
 end
 def test_order_without_delivery_not_enough
  e=[{event: :drop},{event: :appeal_file},{event: :repair_decision,body: :authorized},{event: :deliver,receipt:false}]
  assert_equal :repair_ordered,RithmR9.authority_trace(e)[:final]
 end
 def test_identity_sensitive_quotient
  c=RithmR9.quotient_counterexample
  assert_equal [1,1,1,1],c[:aggregate]
  assert c[:pending_b2_a]
  refute c[:pending_b2_b]
 end
end