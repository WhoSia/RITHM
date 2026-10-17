# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'prefix_bound'
class TestRithmPrefixBound < Minitest::Test
  C=RithmCompositionCourt
  def test_basic_overload_and_deferred_deadline
    a=C.bundle(person:'A',episode:'E',deadline:1)
    b=C.bundle(person:'B',episode:'E',deadline:1)
    assert_equal 1,RithmPrefixBound.min_boost([a,b],capacities:[1])
    assert_equal 0,RithmPrefixBound.min_boost([a,b],capacities:[2])
    c=C.bundle(person:'B',episode:'E',deadline:2)
    assert_equal 0,RithmPrefixBound.min_boost([a,c],capacities:[1,1])
    assert_equal 1,RithmPrefixBound.min_boost([a,c],capacities:[1,0])
  end
  def test_exact_vs_ruby_dynamic_program_small_exhaustive
    count=0
    [1,2,3].each do |h|
      [0,1,2].repeated_permutation(h).each do |caps|
        (1..h).each do |d1|
          (1..h).each do |d2|
            a=C.bundle(person:'A',episode:'E1',deadline:d1)
            b=C.bundle(person:'B',episode:'E1',deadline:d2)
            bound=RithmPrefixBound.min_boost([a,b],capacities:caps)
            assert C.synthesize([a,b],capacities:caps,boost_budget:bound)['win'], [h,caps,d1,d2,bound].inspect
            if bound.positive?
              refute C.synthesize([a,b],capacities:caps,boost_budget:bound-1)['win'], [h,caps,d1,d2,bound].inspect
            end
            count+=1
          end
        end
      end
    end
    assert_equal 282,count
  end
end
