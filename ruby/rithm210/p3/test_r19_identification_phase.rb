require 'minitest/autorun'
require_relative 'r19_identification_phase'
class TestRithm210R19IdentificationPhase < Minitest::Test
  M=Rithm210R19IdentificationPhase
  def test_exact_formula_versus_64_state_value_iteration
    (1..5).each do |n|
      [1,2,3,4,5,10,40].each do |h|
        r=M.independently_check(n:n,horizon:h)
        assert_equal (h/2)*12*(n-4).abs,r[:width]
      end
    end
  end
  def test_welfare_fully_identified_at_n4
    x=M.independently_check(n:4,horizon:40)
    assert_equal 1020,x[:minimum]
    assert_equal 1020,x[:maximum]
    assert_equal 0,x[:width]
  end
  def test_nonzero_width_and_edge_rejection
    assert_equal 240,M.closed_form(n:3,horizon:40)[:width]
    assert_equal 480,M.closed_form(n:2,horizon:40)[:width]
    assert_raises(ArgumentError){M.closed_form(n:0,horizon:40)}
    assert_raises(ArgumentError){M.closed_form(n:4,horizon:0)}
  end
end
