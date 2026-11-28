require 'minitest/autorun'
require_relative 'r66_t38_fiber'
class TestR66T38Fiber < Minitest::Test
  F=RithmT38::Fiber;R=F::R
  def test_cost_and_monotonicity
    s=F.setup;vs=s[:vertices];rng=Random.new(3801)
    40.times do
      w=Array.new(vs.size){rng.rand(1..20)};q=vs.first.each_index.map{|i|vs.each_with_index.sum{|v,j|v[i]*w[j]}/w.sum}
      v,d=F.cost_and_slope(q.first,s[:mean_cost],F::REC,F::H)
      assert_equal R.finite(q,F::REC,F::H),v
      assert_operator d,:>,0;assert_operator d,:<=,s[:slope]
    end
  end
  def test_alias_witness_and_all_events
    s=F.setup;z=11r/1000;w=F.witness(s,[2,3,4,5],z)
    [w[:low],w[:high]].each do |q|
      assert q.all?{|x|x>=0};assert_equal 1,q.sum
      assert_equal 5*F::P,q.each_with_index.sum{|x,i|x*i}
      assert_equal 20*F::P**2,q.each_with_index.sum{|x,i|x*i*(i-1)}
      assert_equal z,F.event(q,[2,3,4,5])
    end
    assert_operator w[:floor],:>,12r/100
    assert_equal w[:improvement],s[:baseline]-R.finite(w[:low],F::REC,F::H)
    assert_equal w[:harm],R.finite(w[:high],F::REC,F::H)-s[:baseline]
    assert_equal w[:floor],F.harm_floor(w[:improvement],w[:harm])
    z=F.audit;assert_equal [[0]],z[:all_binary_events_up_to_complement].select{|x|x[:alias_floor]==0}.map{|x|x[:indices]}
    n=z[:conservative_sample_size_for_no_switch_bound];assert_operator s[:slope]**2,:<,8*n*w[:floor]**2
  end
end
