require 'minitest/autorun'
require_relative 'qi_abc_forward_bootstrap'
class TestRithm210QiABCForwardBootstrap < Minitest::Test
  M = Rithm210QiABCForwardBootstrap
  def fixture
    base = { 1 => [2.0, 3.0], 2 => [4.0] }
    [:markov, :epoch20, :a, :b, :c].to_h do |kind|
      shift = kind == :b ? 1.0 : 0.0
      [kind,base.flat_map { |session,values| values.map do |v|
        {session: session, absolute_error: v + shift,
         squared_error: v + shift, terminal_logloss: v + shift}
      end }]
    end
  end
  def test_paired_session_arithmetic
    result = M.bootstrap([1,2], fixture, draws: 200, seed: 7)
    r = result[:absolute_error]
    assert_equal 3,r[:qi_b_minus_qi_c][:n]
    assert_in_delta 1.0,r[:qi_b_minus_qi_c][:delta],1e-12
    assert_in_delta 0.0,r[:epoch20_minus_markov][:delta],1e-12
    assert_equal [1.0,1.0],r[:qi_b_minus_qi_c][:percentile95]
  end
  def test_reproducibility_and_rejections
    assert_equal M.bootstrap([1,2],fixture,draws:20,seed:14),
                 M.bootstrap([1,2],fixture,draws:20,seed:14)
    assert_raises(ArgumentError){M.bootstrap([],fixture)}
    assert_raises(ArgumentError){M.bootstrap([1],fixture,draws:0)}
    rows=fixture
    rows[:a]=[]
    assert_raises(RuntimeError){M.bootstrap([1,2],rows,draws:5)}
  end
end
