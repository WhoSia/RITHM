require 'minitest/autorun'
require_relative 'ssm_joint_falsifier'
class TestRithm210SSMJointFalsifier < Minitest::Test
  M=Rithm210SSMJointFalsifier
  def test_early_freeze_no_go_and_late_welfare
    sim={early:{zero:0.60177773412562,next_loss:1.7352796739183813},
         late:{zero:0.5031753486757469,next_loss:1.9510322435727268}}
    obs={early:{zero:34.0/154,next_loss:465.0/154},
         late:{zero:150.0/257,next_loss:342.0/257}}
    r=M.compare(simulation:sim,observed:obs)
    refute r[:early][:feasible]
    assert r[:late][:feasible]
    assert_in_delta 0.1619932478,r[:late][:freeze],1e-7
    assert_in_delta 1.6349781938,r[:late][:predicted_next_loss],1e-7
    assert_in_delta 0.3042388942,r[:late][:welfare_error],1e-7
  end
  def test_nonoptimal_baseline_welfare_is_retained_during_freeze
    b={early:{zero:0.2,next_loss:6.0},late:{zero:0.2,next_loss:6.0}}
    o={early:{zero:0.4,next_loss:4.5,current_loss:3.0},
       late:{zero:0.4,next_loss:4.5,current_loss:3.0}}
    r=M.compare(simulation:b,observed:o)
    assert_in_delta 5.25,r[:early][:predicted_next_loss],1e-12
  end
end
