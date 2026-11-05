# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'readonly_symbol_inventory'

class TestRithm210ReadOnlySymbols < Minitest::Test
  I = Rithm210ReadOnlySymbols

  def test_actual_rithm_occupancy_symbols_at_exact_lines
    source = File.read(File.join(__dir__, 'occupancy_churn_bounds.rb'), encoding: 'UTF-8')
    actual = I.definitions(source)
    expected = [
      ['check!', 6], ['possible_pairs', 11], ['gross_range', 17],
      ['possible_gross', 21], ['resource_bounds', 25], ['congestion_cost', 33]
    ]
    assert_equal expected, actual.map { |x| [x[:name], x[:line]] }
  end

  def test_real_micromacro_and_coupling_symbol_counts
    welfare = I.definitions(File.read(File.join(__dir__, 'friction_welfare.rb')))
    coupling = I.definitions(File.read(File.join(__dir__, 'turnover_coupling_witness.rb')))
    assert_equal %w[rational validate stationary? interior_stationary_band social_cost excess_at_zero_bias inertia_bound step pulse_example],
                 welfare.map { |x| x[:name] }
    assert_equal %w[distributions summarize witness], coupling.map { |x| x[:name] }
  end

  def test_lexical_lookalikes_not_counted_as_symbols
    source = "# def fake_comment\n"              "text = 'def fake_string'\n"              "module Sample\n  def actual; end\n  def self.singleton; end\nend\n"
    assert_equal [['actual', 4], ['singleton', 5]], I.definitions(source).map { |x| [x[:name], x[:line]] }
  end

  def test_invalid_and_oversized_source_fail_closed
    assert_raises(ArgumentError) { I.definitions(nil) }
    assert_raises(ArgumentError) { I.definitions('def incomplete(') }
    assert_raises(ArgumentError) { I.definitions('a' * 65_537) }
    assert_equal [], I.definitions("# only comment\n")
  end
end
