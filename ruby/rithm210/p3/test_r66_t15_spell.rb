# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t15_spell'
class T15SpellTest < Minitest::Test
  S=RithmT15::Spell
  def test_survival_equivalence
    (0..40).each { |k| assert_equal S.survival(k),S.renewal_survival(k) }
  end
  def test_duration_decline
    assert_equal Rational(1,2),S.hazard(0)
    assert_equal Rational(3,8),S.hazard(1)
    assert_equal Rational(3,10),S.hazard(2)
    (0...20).each { |k| assert_operator S.hazard(k),:>,S.hazard(k+1) }
  end
  def test_post_switch_discriminator
    assert_equal Rational(5,8),S.after_switch(0,:fixed)
    assert_equal Rational(1,2),S.after_switch(0,:reset)
    assert_equal S.after_switch(1,:fixed),S.after_switch(1,:reset)
    assert_operator S.after_switch(2,:fixed),:<,S.after_switch(2,:reset)
  end
  def test_bad_inputs
    assert_raises(ArgumentError){ S.hazard(-1) }
    assert_raises(ArgumentError){ S.survival(1.2) }
    assert_raises(ArgumentError){ S.after_switch(0,:other) }
  end
end
