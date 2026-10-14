require 'minitest/autorun'
require 'set'
require_relative 'p0r3_queue_court'
class QueueCourtTest < Minitest::Test
  def brute(c)
    best=-Float::INFINITY
    walk=nil
    walk=lambda{|root,u,seen,total,len|c.edges[u].each{|v,w|
      if v==root
        best=[best,(total+w).to_f/(len+1)].max
      elsif !seen.include?(v)
        seen.add(v);walk.call(root,v,seen,total+w,len+1);seen.delete(v)
      end
    }}
    c.states.each_index{|i|walk.call(i,i,Set[i],0,0)}
    best/4.0
  end
  def test_adaptive_policies_against_independent_cycle_enumeration
    {[:sticky,false]=>5.0/12,[:sticky,true]=>0.75,
     [:last_shock,false]=>0.5,[:last_shock,true]=>5.0/6,
     [:parity,false]=>7.0/12,[:parity,true]=>7.0/12}.each{|(p,d),value|
       c=QueueCourt.new(policy:p,delay:d)
       assert_in_delta value,c.maximum_cycle_mean,1e-8
       assert_in_delta value,brute(c),1e-8
       refute c.unsafe
     }
  end
  def test_fixed_bottleneck_is_unsafe
    [false,true].each{|d|c=QueueCourt.new(policy: :fixed0,delay:d)
      assert c.unsafe
      assert_in_delta 3.0,c.maximum_cycle_mean,1e-8
    }
  end
end
