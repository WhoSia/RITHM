require 'minitest/autorun'
require_relative 'factorial_session_randomization'
class TestRithm210FactorialSessionRandomization < Minitest::Test
  M=Rithm210FactorialSessionRandomization
  def test_balanced_randomization_and_seed
    a=M.assignment((1..24).to_a,seed:5)
    assert_equal a,M.assignment((1..24).to_a,seed:5)
    assert_equal [6],a.values.tally.values.uniq
    assert_equal 24,a.keys.size
  end
  def test_difference_in_differences_algebra
    a={1=>:sim_frozen,2=>:sim_refreshed,3=>:seq_frozen,4=>:seq_refreshed}
    x=M.effects(a,{1=>10,2=>9,3=>10,4=>4})
    assert_equal 0.0,x[:schedule_when_frozen]
    assert_equal(-1.0,x[:refresh_under_simultaneous])
    assert_equal(-6.0,x[:refresh_under_sequential])
    assert_equal(-5.0,x[:interaction])
  end
  def test_randomization_unbiased_across_all_24_assignments
    ids=[1,2,3,4]
    potential=ids.to_h{|i|[i,{sim_frozen:i,sim_refreshed:i+1,
      seq_frozen:i+2,seq_refreshed:i+3+i}]}
    target=M.finite_population_interaction(potential)
    estimates=M::ARMS.permutation.map do |perm|
      assignments=ids.zip(perm).to_h
      observed=assignments.to_h{|i,arm|[i,potential[i][arm]]}
      M.effects(assignments,observed)[:interaction]
    end
    assert_equal 24,estimates.size
    assert_in_delta target,estimates.sum/estimates.size.to_f,1e-12
  end
  def test_reject_invalid_designs
    assert_raises(ArgumentError){M.assignment([1,2,3])}
    assert_raises(ArgumentError){M.assignment([1,1,2,3])}
    assert_raises(ArgumentError){M.effects({1=>:sim_frozen},{1=>4})}
    assert_raises(ArgumentError){M.finite_population_interaction({1=>{seq_frozen:2}})}
  end
end
