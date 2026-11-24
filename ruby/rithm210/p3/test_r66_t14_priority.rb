# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t14_priority'
class R66T14PriorityTest < Minitest::Test
  P=RithmT14::Priority
  def axes(x)
    P::L_WEIGHTS.keys.to_h { |k| [k,x] }
  end
  def test_weights_normalized
    assert_equal 1,P::L_WEIGHTS.values.sum
    assert_equal 1,P::E_WEIGHTS.values.sum
  end
  def test_exact_arithmetic
    assert_equal Rational(9525,10000),P.weighted({b:'0.98',d:'0.95',w:'0.94',f:'0.98',r:'0.90'},P::L_WEIGHTS)
  end
  def test_gate_overrides_score
    a=P.rank([{id:'blocked',gate: :blocked,axes:axes(1)},{id:'ready',gate: :ready,axes:axes('0.7')}])
    assert_equal 'ready',a.first[:id]
    refute a.last[:eligible]
  end
  def test_rank_ready_candidates
    a=P.rank([{id:'b',gate: :ready,axes:axes('0.8')},{id:'a',gate: :ready,axes:axes('0.9')}])
    assert_equal %w[a b],a.map { |x| x[:id] }
  end
  def test_reject_invalid_axis
    assert_raises(ArgumentError){P.weighted(axes(2),P::L_WEIGHTS)}
    assert_raises(ArgumentError){P.weighted({},P::L_WEIGHTS)}
  end
  def test_evidence_is_not_recommendation
    x=P.evidence(axes:P::E_WEIGHTS.keys.to_h { |k| [k,'0.8'] },claim:1,generalization:'0.2')
    assert_equal({e:Rational(4,5),c:1,g:Rational(1,5)},x)
  end
end
