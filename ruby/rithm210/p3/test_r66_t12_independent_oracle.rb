# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t12_independent_oracle'
class R66T12OracleTest < Minitest::Test
  K=RithmT12::Kernel
  S=RithmT12::Schedules
  O=RithmT12::Oracle
  def test_64_labelled_vector_oracle
    [S.common,S.independent,S.fixed_count(3)].each do |schedule|
      p,_=K.transition(schedule)
      7.times { |n| assert_equal p[n],O.row(n,schedule) }
    end
  end
  def test_fractional_effort_oracle
    schedule=S.fixed_count(3)
    p,_=K.transition(schedule,Rational(2,3))
    [0,4,5,6].each { |n| assert_equal p[n],O.row(n,schedule,effort:Rational(2,3)) }
  end
end
