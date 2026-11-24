# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t14_persistent'
class R66T14PersistentTest < Minitest::Test
  P=RithmT14::Persistent;K=RithmT14::Kernel;S=RithmT12::Schedules
  def test_type_law
    7.times { |n| assert_equal 1,P.type_law(n).sum { |x| x[2] } }
  end
  def test_first_transition_matches_fresh_types
    [S.common,S.independent,S.fixed_count(3)].each do |w|
      7.times do |n|
        assert_equal K.forecast(n0:n,horizon:2,schedule:w,mechanism: :cognitive),P.forecast(n0:n,horizon:2,schedule:w)
      end
    end
  end
  def test_permanent_types_change_long_horizon
    w=S.fixed_count(3)
    a=P.forecast(n0:5,horizon:40,schedule:w)
    b=K.forecast(n0:5,horizon:40,schedule:w,mechanism: :cognitive)
    refute_equal a,b
    assert_operator a[:congestion],:>,b[:congestion]
  end
  def test_immobile_group
    assert_equal [[1]],P.transition(5,1,S.independent)
  end
  def test_no_correction_lower_bound
    # P(all five initial A actors are high-cost)=1/32: A=5 stays forever.
    a=P.forecast(n0:5,horizon:40,schedule:S.common)
    assert_operator a[:final][5],:>=,Rational(1,32)
    assert_operator a[:congestion],:>=,Rational(120,32)
  end
  def test_invalid_type_counts
    assert_raises(ArgumentError){P.transition(7,0,S.common)}
  end
end
