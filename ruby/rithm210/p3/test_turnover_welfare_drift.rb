require 'minitest/autorun'
require_relative 'turnover_welfare_drift'
class TestRithm210TurnoverWelfareDrift < Minitest::Test
  M=Rithm210TurnoverWelfareDrift
  def test_all_feasible_exact_identities
    (0..6).each do |n|
      (0..(6-n)).each do |u|
        (0..n).each do |d|
          v=M.score(n,u,d)
          assert_equal v[:subsequent]-v[:current],v[:drift]+v[:quadratic]
          assert_operator v[:quadratic],:>=,0
        end
      end
    end
  end
  def test_optimum_movement_is_pure_quadratic
    (0..2).each do |u|
      (0..4).each do |d|
        v=M.score(4,u,d)
        assert_equal 0,v[:drift]
        assert_equal 3*(u-d)**2,v[:delta]
      end
    end
  end
  def test_toward_and_away
    assert M.score(2,1,0)[:toward]
    assert M.score(4,1,0)[:away]
    refute M.score(4,1,1)[:away]
  end
  def test_invalid_turnovers
    assert_raises(ArgumentError){M.score(4,3,0)}
    assert_raises(ArgumentError){M.score(4,0,5)}
  end
end
