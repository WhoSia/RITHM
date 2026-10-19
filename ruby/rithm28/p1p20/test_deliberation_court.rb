# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'deliberation_court'
class TestDeliberationCourt < Minitest::Test
 M=RithmDeliberationCourt
 def test_three_simultaneous_inspections_cycle
  a=M.simulate(initial:[0,0,0],q:[0,0,0],k:[0,0,0],horizon:4)
  assert_equal [9,9,9,9,9],a.fetch('costs')
  assert_equal [[0,0,0],[1,1,1],[0,0,0]],a.fetch('states').first(3)
 end
 def test_single_inspector_stabilizes
  a=M.simulate(initial:[0,0,0],q:[0,2,2],k:[0,0,0],horizon:4)
  assert_equal [9,5,5,5,5],a.fetch('costs')
 end
 def test_friction_and_deliberation_are_separable
  qcase=M.update([0,0,0],q:[1,2,2],k:[0,0,0])
  kcase=M.update([0,0,0],q:[0,0,0],k:[1,2,2])
  assert_equal qcase.fetch('routes'),kcase.fetch('routes')
  assert_equal 1,qcase.fetch('deliberation_spend')
  assert_equal 1,kcase.fetch('switch_spend')
  assert_equal 0,qcase.fetch('switch_spend')
 end
 def test_strict_threshold_at_two
  assert_equal [0,0,0],M.update([0,0,0],q:[2,2,2],k:[0,0,0]).fetch('routes')
  assert_equal [1,1,1],M.update([0,0,0],q:[1,1,1],k:[0,0,0]).fetch('routes')
 end
 def test_sequential_order_revises_beliefs
  assert_equal [1,0,0],M.update([0,0,0],q:[0,0,0],k:[0,0,0],schedule: :sequential).fetch('routes')
 end
 def test_exhaustive_input_and_state_conservation
  [0,1,2].repeated_permutation(3).each do |q|
    [0,1,2].repeated_permutation(3).each do |k|
      [0,1].repeated_permutation(3).each do |s|
        [:parallel,:sequential].each do |schedule|
          u=M.update(s,q:q,k:k,schedule:schedule)
          assert_equal 3,u.fetch('routes').size
          assert [5,9].include?(u.fetch('social_cost'))
        end
      end
    end
  end
 end
end
