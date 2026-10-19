# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'phase_grid'
class TestPhaseGrid < Minitest::Test
 def test_exact_two_round_parameter_grid
  r=Rithm29PhaseGrid.scan
  assert_equal 12,r.length
  assert r.all?{|x|x[:complete]}
  assert r.all?{|x|x[:maximum]>=x[:minimum]}
  a=r.find{|x|x[:fee]==1&&x[:switch]==Rational(1,2)}
  assert_equal Rational(17,2),a[:minimum]
  assert_equal 10,a[:maximum]
 end
end
