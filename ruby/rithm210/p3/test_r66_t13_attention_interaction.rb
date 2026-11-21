# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t13_attention_interaction'
class T13AttentionInteractionTest < Minitest::Test
  X=RithmT13::AttentionInteraction
  def test_more_attention_harms_shared_but_helps_independent
    c=X.contrast
    assert_operator c[:effect_by_clock][:common],:>,0
    assert_operator c[:effect_by_clock][:independent],:<,0
    assert_operator c[:effect_by_clock][:fixed_three],:<,0
  end
  def test_interaction_positive
    assert_operator X.contrast[:interaction_shared_minus_independent],:>,0
  end
  def test_same_lower_higher_rejected
    assert_raises(ArgumentError) { X.contrast(low:1,high:1) }
  end
  def test_fraction_exact
    assert_kind_of Rational,X.contrast[:effect_by_clock][:common]
  end
end
