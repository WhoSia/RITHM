require 'minitest/autorun'
require_relative 'welfare_bootstrap'
class TestRithm210WelfareBootstrap < Minitest::Test
  M=Rithm210WelfareBootstrap
  def fixture
    {'by_session'=>(1..24).to_h do |s|
      [s.to_s,{
        'baseline'=>{'n'=>234,'logloss'=>1.0,'mse'=>1.0},
        'online_20'=>{'n'=>234,'logloss'=>0.9,'mse'=>2.0},
        'online_80'=>{'n'=>234,'logloss'=>1.1,'mse'=>0.5}}]
    end}
  end
  def test_exact_constant_session_deltas
    r=M.run(fixture,draws:100)
    assert_in_delta(-0.1,r[:logloss20][:point],1e-12)
    assert_in_delta(+0.1,r[:logloss80][:point],1e-12)
    assert_in_delta(+1.0,r[:mse20][:lower],1e-12)
    assert_in_delta(-0.5,r[:mse80][:upper],1e-12)
    assert_equal 24,r[:logloss20][:sessions_improved]
    assert_equal 0,r[:mse20][:sessions_improved]
  end
  def test_deterministic_seed
    assert_equal M.run(fixture,draws:100),M.run(fixture,draws:100)
  end
  def test_reject_incomplete_source
    bad=fixture
    bad['by_session'].delete('24')
    assert_raises(RuntimeError){M.run(bad,draws:100)}
  end
end
