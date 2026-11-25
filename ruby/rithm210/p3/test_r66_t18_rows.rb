require 'minitest/autorun'
require_relative 'r66_t18_rows'
class TestR66T18Rows < Minitest::Test
  T=RithmT18
  def test_equal_prior_predictive
    (0..5).each do |k|
      f=T::Rows.new; p=f.observe(k); q=T::Filter.new([0.45]); q.observe(:a,9,disclosed_k:k)
      p.zip(q.marginal).each { |a,b| assert_in_delta a,b,1e-12 }
    end
  end
  def test_count_updates_and_no_zero_mass
    f=T::Rows.new
    before=f.observe(4)[4]
    20.times { f.observe(4) }
    assert_operator f.pred[4],:>,before
    assert_in_delta 1,f.pred.sum,1e-12
    assert f.pred.all?(&:positive?)
    assert_raises(ArgumentError){f.observe(6)}
  end
  def test_sticky_exact_and_fixed_equivalence
    T::CLOCKS.each do |clock|
      [0.4,1.0].each do |r|
        t=T.tape(303,40)
        {fixed:[0.45],sticky:[0.25,0.65]}.each do |m,g|
          expected=T.run(n:5,tape:t,clock:clock,grid:g,disclosure:1,response:r)[:cost]
          assert_equal expected,T::Full.run(tape:t,clock:clock,response:r,mode:m)[:cost]
        end
      end
    end
  end
  def test_replay_same_paths
    paths=Array.new(39){Array.new(6,4)}
    scores=T::Full.replay(paths)
    assert_operator scores[:rows],:<,scores[:fixed]
    assert_operator scores[:sticky],:<,scores[:fixed]
  end
end
