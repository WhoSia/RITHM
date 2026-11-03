require 'minitest/autorun'
require_relative 'longitudinal_identity_audit'
class TestRithm210LongitudinalIdentity < Minitest::Test
  M=Rithm210LongitudinalIdentity
  def synthetic
    groups={}
    pattern=Array.new(4,1)+Array.new(16,2)+Array.new(4,3)
    pattern.each_with_index do |group_count,i|
      s=i+1
      (1..group_count).each do |g|
        ids=(1..6).map{|j|100*s+10*g+j}
        (2..4).each do |section|
          (1..39).each do |period|
            groups[[s,section,g,period]]=ids.map{|id|{'ID'=>id.to_s}}
          end
        end
      end
    end
    groups
  end
  def test_stable_288_people_48_groups
    result=M.audit(synthetic)
    assert_equal 288,result[:participants]
    assert_equal 48,result[:unchanged_group_compositions]
    assert_equal 117,result[:observations_per_person]
  end
  def test_detect_group_membership_change
    g=synthetic
    g[[5,3,1,1]][0]['ID']='999999'
    assert_raises(RuntimeError){M.audit(g)}
  end
end
