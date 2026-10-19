# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'mixed_support'
class TestMixedSupport < Minitest::Test
 def test_symmetric_support_with_full_deviation_check
   z=Rithm29Correspondence::STATES.to_h{|s|[s,[0,0]]}
   r=Rithm29MixedSupport.symmetric_two_support(z,prev:[0,0],fee:1,switch:0,wrong:2)
   assert r.all?{|x|x[:probability_b].between?(0,1)}
   assert r.all?{|x|x[:social].is_a?(Rational)}
 end
 def test_unsupported_asymmetric_memory_refused
   z=Rithm29Correspondence::STATES.to_h{|s|[s,[0,0]]}
   assert_raises(ArgumentError){Rithm29MixedSupport.symmetric_two_support(z,prev:[0,1],fee:1,switch:0)}
 end
end
