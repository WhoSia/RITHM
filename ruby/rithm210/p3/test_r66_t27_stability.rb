require 'minitest/autorun'
require_relative 'r66_t27_stability'
class TestR66T27Stability < Minitest::Test
  S=RithmT27::Stability;C=RithmT27::Compare
  def test_actual_refits_and_small_sample_guard
    k=[[1,0,0],[1,0,0,3],[1,0,0,0],[1,0,0,3,0],[1,0,0,3,2],[1,0,0,3,1],[1,0,0,3,0],[1,0,0,3,0,2,1],[1,0,0,3,0,2,1,0]]
    rows=[['a',k,0],['b',k,1],['c',k,1],['c',k,0]]
    actual=S.deletion(rows)
    expected=%w[a b c].map{|sid|C.evaluate(rows.reject{|r|r.first==sid})[:contrasts]['behavior_minus_both'][:mean]}
    expected.minmax.zip(actual['behavior_minus_both'][:range]).each{|a,b|assert_in_delta a,b,1e-12}
    assert_equal expected.count(&:negative?),actual['behavior_minus_both'][:negative]
    assert_equal 3,actual['behavior_minus_both'][:refits]
    assert_raises(RuntimeError){S.deletion(rows.take(2))}
  end
  def test_grouped_deletion_matches_direct_refit_on_synthetic_sessions
    rng=Random.new(2702)
    rows=5.times.flat_map do |sid|
      80.times.map do
        b=[rng.rand(3),rng.rand(2),rng.rand(2)];o=rng.rand(3);h=rng.rand(2);d=rng.rand(5);f=rng.rand(4);g=rng.rand(4)
        ks=[b,b+[o],b+[h],b+[o,h],b+[o,d],b+[o,f],b+[o,g],b+[o,h,d,f],b+[o,h,d,f,g]]
        [sid,ks,rng.rand(2)]
      end
    end
    actual=S.deletion(rows)
    expected=(0...5).map{|sid|C.evaluate(rows.reject{|r|r.first==sid})[:contrasts].transform_values{|v|v[:mean]}}
    actual.each do |key,v|
      x=expected.map{|h|h.fetch(key)}
      x.minmax.zip(v[:range]).each{|a,b|assert_in_delta a,b,1e-12}
      assert_equal x.count(&:negative?),v[:negative]
    end
  end
end
