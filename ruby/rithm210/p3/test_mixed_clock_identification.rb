require 'minitest/autorun'
require_relative 'mixed_clock_identification'
class TestMixedClockIdentification < Minitest::Test
  M=Rithm210MixedClockIdentification
  def test_action_types_separable_off_equilibrium
    (0..6).each do |n|
      r=M.types(current:n)
      assert_equal n!=4,r[:disjoint]
      if n!=4
        assert_equal :synchronous,M.identified_clock(current:n,next_count:r[:sync_next])
        r[:async_next].each{|m|assert_equal :asynchronous,M.identified_clock(current:n,next_count:m)}
      end
    end
  end
  def test_equilibrium_provides_no_clock_information
    assert_equal :unidentified,M.identified_clock(current:4,next_count:4)
    assert_equal 0,M.fisher_information_per_observation(current:4,sync:Rational(1,2))
    assert_equal 0,M.fisher_information_per_observation(current:4,sync:1)
    assert_equal :outside_model_support,M.identified_clock(current:4,next_count:5)
  end
  def test_off_equilibrium_fisher_information
    (0..6).reject{|n|n==4}.each do |n|
      assert_equal Rational(4),M.fisher_information_per_observation(current:n,sync:Rational(1,2))
    end
    assert_raises(ArgumentError){M.fisher_information_per_observation(current:3,sync:0)}
  end
end
