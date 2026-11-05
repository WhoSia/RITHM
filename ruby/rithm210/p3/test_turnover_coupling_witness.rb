require 'minitest/autorun'
require_relative 'turnover_coupling_witness'
class TestTurnoverCouplingWitness < Minitest::Test
  M=Rithm210TurnoverCouplingWitness
  def test_same_occupancy_and_actor_marginals_but_distinct_tail_risks
    a=M.witness.fetch(:shock);b=M.witness.fetch(:compensated)
    assert_equal [Rational(1,2),Rational(1,2),0,0,Rational(1,2),Rational(1,2)],a[:marginal]
    assert_equal a[:marginal],b[:marginal]
    assert_equal({4=>1},a[:next_occupancy_distribution])
    assert_equal a[:next_occupancy_distribution],b[:next_occupancy_distribution]
    assert_equal 2,a[:expected_gross]
    assert_equal a[:expected_gross],b[:expected_gross]
    assert_equal 4,a[:gross_variance]
    assert_equal 0,b[:gross_variance]
    assert_equal 8,a[:expected_gross_squared]
    assert_equal 4,b[:expected_gross_squared]
    assert_equal Rational(1,2),a[:p_gross_ge_four]
    assert_equal 0,b[:p_gross_ge_four]
  end
  def test_identical_marginals_identify_mean_linear_switching_cost
    a=M.witness[:shock];b=M.witness[:compensated]
    [Rational(1,3),Rational(7,5)].each{|k|assert_equal k*a[:expected_gross],k*b[:expected_gross]}
  end
  def test_malformed_distribution_rejected
    assert_raises(ArgumentError){M.summarize({[0]=>Rational(1,3)})}
    assert_raises(ArgumentError){M.summarize({[0,0]=>1})}
    assert_raises(ArgumentError){M.summarize({[7]=>1})}
  end
end
