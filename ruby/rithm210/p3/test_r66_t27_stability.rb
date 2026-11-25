require 'minitest/autorun'
require_relative 'r66_t27_stability'
class TestR66T27Stability < Minitest::Test
  S=RithmT27::Stability;C=RithmT27::Compare
  def test_actual_refits_and_small_sample_guard
    k=[[1,0,0],[1,0,0,3],[1,0,0,0],[1,0,0,3,0],[1,0,0,3,2],[1,0,0,3,1],[1,0,0,3,0],[1,0,0,3,0,2,1],[1,0,0,3,0,2,1,0]]
    rows=[['a',k,0],['b',k,1],['c',k,1],['c',k,0]]
    actual=S.deletion(rows)
    expected=%w[a b c].map{|sid|C.evaluate(rows.reject{|r|r.first==sid})[:contrasts]['behavior_minus_both'][:mean]}
    assert_equal expected.minmax,actual['behavior_minus_both'][:range]
    assert_equal expected.count(&:negative?),actual['behavior_minus_both'][:negative]
    assert_equal 3,actual['behavior_minus_both'][:refits]
    assert_raises(RuntimeError){S.deletion(rows.take(2))}
  end
end
