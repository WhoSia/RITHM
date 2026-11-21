# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t13_counterexamples'
class T13LapseSensitivityTest < Minitest::Test
  C=RithmT13::Counterexamples
  def schedule_laws
    s=RithmT12::Schedules
    {common:s.common,independent:s.independent,fixed_three:s.fixed_count(3)}
  end
  def sweep(n0:,attention:,threshold:,lapse:)
    schedule_laws.transform_values do |s|
      RithmT13::Kernel.total(n0:n0,horizon:40,schedule:s,attention:attention,threshold:threshold,lapse:lapse)
    end
  end
  def test_zero_lapse_kappa_two_absorbing_optimum
    x=sweep(n0:4,attention:Rational(1,2),threshold:2,lapse:0)
    assert x.values.all? { |v| v[:congestion]==0 && v[:gross_switches]==0 }
    y=sweep(n0:4,attention:Rational(1,2),threshold:2,lapse:Rational(1,50))
    assert y.values.all? { |v| v[:congestion]>0 }
  end
  def test_lapse_rate_reverses_policy_ranking
    [Rational(1,100),Rational(1,50)].each do |lapse|
      x=sweep(n0:4,attention:Rational(1,2),threshold:2,lapse:lapse)
      assert_operator x[:common][:congestion],:<,x[:fixed_three][:congestion]
    end
    x=sweep(n0:4,attention:Rational(1,2),threshold:2,lapse:Rational(1,20))
    assert_operator x[:fixed_three][:congestion],:<,x[:common][:congestion]
  end
  def test_no_lapses_but_off_equilibrium_still_nontrivial
    x=sweep(n0:5,attention:Rational(1,2),threshold:0,lapse:0)
    assert_operator x[:fixed_three][:congestion],:<,x[:independent][:congestion]
    assert_operator x[:independent][:congestion],:<,x[:common][:congestion]
    assert x.values.all? { |v| v[:congestion]>0 }
  end
end
