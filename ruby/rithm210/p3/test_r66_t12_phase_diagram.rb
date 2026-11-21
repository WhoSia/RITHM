# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t12_phase_diagram'
class R66T12PhaseDiagramTest < Minitest::Test
  D=RithmT12::PhaseDiagram
  K=RithmT12::Kernel
  def test_all_prefixes_equal_independent_forecasts
    seq=D.trajectories(n0:4,max_horizon:12)
    schedules={common:RithmT12::Schedules.common,independent:RithmT12::Schedules.independent,
               staggered_three:RithmT12::Schedules.fixed_count(3)}
    seq.each do |name,rows|
      rows.each do |row|
        exact=K.forecast(n0:4,horizon:row[:horizon],schedule:schedules[name])
        assert_equal exact[:congestion],row[:congestion]
        assert_equal exact[:gross_switches],row[:revisions]
      end
    end
  end
  def test_h2_common_better_h40_worse
    t=D.trajectories(n0:4)
    assert_operator t[:common][1][:congestion],:<,t[:independent][1][:congestion]
    assert_operator t[:common][-1][:congestion],:>,t[:independent][-1][:congestion]
  end
  def test_crossover_at_h3
    t=D.trajectories(n0:4)
    assert_equal({first_positive_horizon:3,first_negative_horizon:2},D.crossover(t,:common,:independent))
    assert_equal({first_positive_horizon:2,first_negative_horizon:3},D.crossover(t,:staggered_three,:independent))
  end
  def test_fee_indifference_zero_denominator
    a={congestion:Rational(1),revisions:Rational(1)}
    b={congestion:Rational(2),revisions:Rational(1)}
    assert_nil D.fee_indifference(a,b)
  end
  def test_fee_indifference_exact_fraction
    a={congestion:Rational(4),revisions:Rational(2)}
    b={congestion:Rational(2),revisions:Rational(3)}
    assert_equal 2,D.fee_indifference(a,b)
  end
end
