require 'minitest/autorun'
require_relative 'section_order_audit'
class TestRithm210SectionOrderAudit < Minitest::Test
  Q=Rithm210SectionOrderAudit
  def test_balanced_synthetic_24_session_design
    rows=(1..24).flat_map do |session|
      (2..4).map do |section|
        {session:session,section:section,treatment:section-1,
          joint1:1.0,joint0:1.0}
      end
    end
    result=Q.summarize(rows)
    assert_equal 24,result[:sessions]
    assert_equal({'1-2-3'=>24},result[:treatment_sequence_counts])
    assert_equal 3,result[:assignment_counts].size
    assert result[:section_treatment_losses].all?{|r|r[:joint_delta]==0.0}
  end
  def test_invalid_duplicate_treatment_assignment_rejected
    rows=(1..24).flat_map do |session|
      (2..4).map{|section|{session:session,section:section,treatment:1,joint1:1.0,joint0:1.0}}
    end
    assert_raises(RuntimeError){Q.summarize(rows)}
  end
end
