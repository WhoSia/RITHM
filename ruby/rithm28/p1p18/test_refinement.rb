# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'refinement'
class TestRefinement < Minitest::Test
  M=RithmRefinement
  def c(h:5,b:1,delay:1,revoke:0,restore:6,cost:0)
    {'horizon'=>h,'budget'=>b,'probe_cost'=>cost,'delay'=>delay,'revoke_at'=>revoke,'restore_at'=>restore}
  end
  def test_free_information_refinement_grid
    count=0
    [4,5].each do |h|
      [0,1,2].each do |b|
        [1,2].each do |delay|
          (0..h+1).each do |restore|
            stronger=c(h:h,b:b,delay:delay,revoke:0,restore:restore)
            weaker=c(h:h,b:b,delay:delay,revoke:0,restore:h+1)
            assert M.compare(weaker,stronger).fetch('inclusion_maintained')
            count+=1
          end
        end
      end
    end
    assert_equal 132,count
  end
  def test_delayed_information_may_be_too_late
    refute M.decision(c(restore:5))
    assert M.decision(c(restore:4))
  end
  def test_different_physics_rejected
    assert_raises(ArgumentError){M.compare(c, c(b:2,restore:4))}
    assert_raises(ArgumentError){M.compare(c, c(cost:1,restore:4))}
  end
  def test_invalid_refinement_rejected
    assert_raises(ArgumentError){M.compare(c(restore:4),c(restore:5))}
  end
end
