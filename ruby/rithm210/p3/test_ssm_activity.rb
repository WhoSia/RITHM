require 'minitest/autorun'
require_relative 'ssm_activity'
class TestRithm210GenerativeSSMActivity < Minitest::Test
  def test_no_change_to_author_table7_statistics
    x=Rithm210GenerativeSSM
    a=x.simulate_one(treatment:3,model: :ssm5,rng:Random.new(123))
    b=x.simulate_one(treatment:3,model: :ssm5,rng:Random.new(123),activity:true)
    assert_equal a,b.reject{|k,v|k==:activity}
  end
  def test_activity_bounds
    result=Rithm210GenerativeSSMActivity.run(replicates:80,seed:20261104)
    assert_equal 6,result[:results].size
    result[:results].each_value do |data|
      data.each_value do |cell|
        assert cell[:no_switch_rate].between?(0,1)
        assert cell[:next_loss]>=0
      end
    end
  end
end
