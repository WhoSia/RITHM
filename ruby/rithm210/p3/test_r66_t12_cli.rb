# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t12_cli'
class R66T12CLITest < Minitest::Test
  def test_three_named_policies
    r=RithmT12::CLI.run(horizon:3)
    assert_equal %i[common independent staggered_three],r[:results]['4'].keys
    assert_match(%r{^1/2},r[:per_actor_opportunity])
  end
  def test_40_horizon_report
    scores=RithmT12::CLI.run[:results]['4']
    assert_operator scores[:staggered_three][:congestion],:<,scores[:independent][:congestion]
    assert_operator scores[:independent][:congestion],:<,scores[:common][:congestion]
  end
  def test_fee_in_summary
    r=RithmT12::CLI.run(horizon:3,fee:1)
    r[:results]['5'].each_value do |v|
      assert_in_delta v[:congestion]+v[:expected_switches],v[:welfare_with_fee],1e-7
    end
  end
end
