# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'price_frontier'
class TestPriceFrontier < Minitest::Test
 def test_complete_rational_price_scan
  r=RithmPriceFrontier.scan
  assert_equal 17,r.fetch('grid').length
  assert r.fetch('grid').all?{|x|x.fetch('full_profiles')==216}
  at_one_sixteenth=r.fetch('grid').find{|x|x.fetch('q')=='1/16'}
  assert_equal 3,at_one_sixteenth.fetch('pure_count')
  assert_equal '95/16',at_one_sixteenth.fetch('best_cost')
  assert_equal '109/16',at_one_sixteenth.fetch('worst_cost')
  assert_equal true,at_one_sixteenth.fetch('has_welfare_inferior_pure')
 end
end
