require 'minitest/autorun'
require_relative 'r23_actor_memory'
class TestR23ActorMemory < Minitest::Test
  M=Rithm210R23ActorMemory
  def test_prior_only_memory_updates
    a=M::State.new
    assert_equal 0,a.periods
    assert_in_delta 0.5,a.frequency(1.0),1e-12
    assert_in_delta 0.5,a.markov(5.0),1e-12
    a.update(1)
    assert_in_delta 2.0/3,a.frequency(1.0),1e-12
    assert_in_delta 0.8,a.markov(5.0),1e-12
    a.update(0)
    assert_in_delta 0.5,a.frequency(1.0),1e-12
    assert_in_delta 1.5/3.5,a.frequency(0.5),1e-12
    assert_in_delta 0.2,a.markov(5.0),1e-12
    a.update(1)
    assert_in_delta 2.0/3,a.markov(5.0),1e-12
  end
  def test_unique_33_candidates
    cs=M.candidates
    assert_equal 33,cs.size
    assert_equal 33,cs.map{|cfg|M.label(cfg)}.uniq.size
    assert_includes cs,[1.0,5.0,0.0]
    assert_includes cs,[1.0,5.0,1.0]
  end
  def test_forecast_is_convex_and_valid
    a=M::State.new;a.update(1)
    assert_in_delta 0.7,M.forecast(a,[1.0,5.0,0.25]),1e-12
    assert_raises(ArgumentError){a.update(2)}
  end
end
