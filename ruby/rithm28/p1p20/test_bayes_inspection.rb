# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'bayes_inspection'
class TestBayesInspection < Minitest::Test
 M=RithmBayesInspection
 def j(p:2,l:4,k:0,q:1)
  M.judge(prior_numerator:p,loss:l,switch_cost:k,inspection_cost:q)
 end
 def test_true_value_of_information
  a=j
  assert_equal 'inspect',a.fetch('decision')
  assert_equal 8,a.fetch('stop_expected_cost_numerator')
  assert_equal 4,a.fetch('inspect_expected_cost_numerator')
 end
 def test_tied_value_no_inspection
  assert_equal 'stop',j(q:2).fetch('decision')
 end
 def test_switching_cost_changes_value_of_inspection
  assert_equal 'inspect',j(k:2,q:0).fetch('decision')
  assert_equal 'stop',j(k:2,q:1).fetch('decision')
 end
 def test_no_reason_to_observe_if_switching_prohibitively_costly
  [0,1,2,3,4].each{|p|assert_equal 'stop',j(p:p,k:4,q:0).fetch('decision')}
 end
 def test_full_finite_grid
  (0..4).each do |p|
   (0..6).each do |k|
    (0..6).each do |q|
     a=j(p:p,k:k,q:q)
     assert_equal(a.fetch('inspect_expected_cost_numerator')<a.fetch('stop_expected_cost_numerator'),
       a.fetch('decision')=='inspect')
     assert_operator a.fetch('stop_expected_cost_numerator'),:>=,0
    end
   end
  end
 end
end
