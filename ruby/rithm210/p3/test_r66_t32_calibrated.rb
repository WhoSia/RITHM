require 'minitest/autorun'
require_relative 'r66_t32_calibrated'
class TestR66T32Calibrated < Minitest::Test
  C=RithmT32::Calibrated;K=RithmT31::Coupling
  def test_extrema_against_exact_reference
    rng=Random.new(3201)
    100.times do
      p=Array.new(6){rng.rand(0..20)/20r};lo,hi=C.extremes(p.map(&:to_f))
      [lo,hi].zip([K.lower(p),K.upper(p)]).each do |a,b|
        a.zip(K.occupancy(b,6)).each{|x,y|assert_in_delta x,y,1e-12}
        assert_in_delta 1,a.sum,1e-12
      end
      C::WEIGHTS.each do |w|
        q=C.joint(C.laws(p.map(&:to_f)),w);assert_in_delta 1,q.sum,1e-12
        assert_in_delta p.sum,q.each_with_index.sum{|x,k|x*k},1e-12
      end
    end
  end
  def test_session_exclusion_and_calibration
    sessions=(1..24).to_a
    sessions.each do |outer|
      t,c=C.split(sessions,outer,8);assert_equal 15,t.size;assert_equal 8,c.size;assert_empty t&c;refute_includes t+c,outer
      assert_equal sessions.sort,(t+c+[outer]).sort
    end
    assert_equal 0.3,C.transform(0.3,0,1)
    assert_operator C.transform(0.3,0.2,1),:>,0.3
    assert_equal 0,C.transform(0,1,1);assert_equal 1,C.transform(1,-1,1)
    assert_raises(ArgumentError){C.transform(0.5,0,0)}
  end
  def test_optimized_selection_matches_direct_scoring
    rng=Random.new(3202)
    cal=3.times.map{Array.new(10){[Array.new(6){0.01+0.98*rng.rand},Array.new(6){rng.rand(2)}]}}
    m=C::GRID.min_by{|o,s|cal.sum{|r|C.score(r,o,s,0)[:individual_logloss]}}
    w0=C::WEIGHTS.min_by{|w|cal.sum{|r|C.score(r,0,1,w)[:group_logloss]}}
    w1=C::WEIGHTS.min_by{|w|cal.sum{|r|C.score(r,*m,w)[:group_logloss]}}
    assert_equal [m,w0,w1],C.select(cal)
  end
  def test_base_identity_and_guard
    p=[0.2,0.4,0.6,0.8,0.9,0.3];a=[0,1,0,1,1,0];r=C.score([[p,a]],0,1,0)
    g=C::G.metrics(p,a);assert_in_delta g[:logloss],r[:group_logloss],1e-12
    assert_in_delta g[:predicted_cost],r[:predicted_cost],1e-12
    assert_in_delta g[:pair_residual],r[:pair_residual],1e-12
    assert_raises(ArgumentError){C.split([1,2],1,1)}
  end
end
