require 'minitest/autorun'
require_relative 'welfare_probability'
class TestRithm210WelfareProbability < Minitest::Test
  M=Rithm210WelfareProbability
  def test_next_welfare_law_and_exact_mean
    actors=[{'RouteA'=>'0'},{'RouteA'=>'1'}]
    law=M.law(actors,[0.5,0.5],4)
    assert_in_delta 0.5,law.fetch(0),1e-12
    assert_in_delta 0.5,law.fetch(3),1e-12
    score=M.scoring(law,0)
    assert_in_delta Rational(3,2),score[:mean],1e-12
    assert_in_delta Math.log(2),score[:logloss],1e-12
    assert_in_delta 2.25,score[:squared_error],1e-12
  end
  def test_all_zero_switching_preserves_occupancy
    actors=[{'RouteA'=>'0'},{'RouteA'=>'1'}]
    law=M.law(actors,[0.0,0.0],4)
    assert_in_delta 1.0,law.fetch(0),1e-12
    assert_equal 1,law.size
  end
  def test_cannot_score_impossible_welfare_category
    assert_raises(RuntimeError){M.scoring({0=>1.0},3)}
  end
end
