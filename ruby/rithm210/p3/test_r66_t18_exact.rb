require 'minitest/autorun'
require_relative 'r66_t18_exact'
class TestR66T18Exact < Minitest::Test
  E=RithmT18::Exact
  def test_strict_interior_escape_and_history_discriminator
    assert_operator E.gain([4]),:<,0
    assert_operator E.gain([4,4]),:<,0
    assert_operator E.gain([4,4,4]),:>,0
    assert_operator E.gain([4,3,4]),:<,0
    [[4,4,4],[4,3,4]].each do |history|
      f=RithmT18::Filter.new([0.25,0.65]); g=nil
      history.each { |k| g=f.observe(:a,9,disclosed_k:k) }
      assert_in_delta E.gain(history).to_f,g,1e-12
    end
  end
  def test_exact_common_matches_labelled_tape_paths
    # all common opportunities forced on/off via tape shared draw, payoff emissions arbitrary.
    (1..9).each do |h|
      costs=(0...(1<<(h-1))).map do |mask|
        tape=Array.new(h-1){|t| [Array.new(6,3),Array.new(6,0),Array.new(6,0),Array.new(6,0),mask[t]==1 ? 0.0 : 0.9]}
        RithmT18.run(n:5,tape:tape,clock: :common,grid:[0.25,0.65],disclosure:1,response:1)[:cost]
      end
      assert_equal Rational(costs.sum,costs.size),E.exact_common(horizon:h)[:expected_cost]
    end
    assert_operator E.exact_common[:expected_cost],:>,120
  end
end
