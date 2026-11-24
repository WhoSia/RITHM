# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t15_prior_audit'
class T15PriorTest < Minitest::Test
  A=RithmT15::PriorAudit
  def test_t14_values
    [:a,:b].each do |r|
      v=RithmT14::Decision.values(r); x=A.values(r,Rational(19,20))
      assert_equal v[:net_prior_gain],x[:net]
      assert_equal v[:value_of_information],x[:evsi]
    end
  end
  def test_boundary
    assert_equal 0,A.values(:b,Rational(9,10))[:net]
    refute A.equivalent?(Rational(899,1000))
    assert A.equivalent?(Rational(9,10))
    assert A.equivalent?(Rational(999,1000))
    refute A.equivalent?(1)
  end
  def test_closed_form
    (0..100).each do |k|
      l=Rational(k,100)
      a=A.values(:a,l); b=A.values(:b,l)
      assert_equal (-3-5*l)/(3+l),a[:net]
      assert_equal (18-20*l)/(3-l),b[:net]
      assert_equal 29*(1-l)/(7*(3+l)),a[:evsi]
      assert_equal 132*(1-l)/(7*(3-l))-[b[:net],0].max,b[:evsi]
      assert_equal l>=Rational(9,10) && l<1,A.equivalent?(l)
    end
  end
  def test_invalid_prior
    assert_raises(ArgumentError){A.values(:a,2)}
    assert_raises(ArgumentError){A.values(:other,0)}
  end
end
