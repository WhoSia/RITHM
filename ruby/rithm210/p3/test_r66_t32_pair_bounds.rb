require 'minitest/autorun'
require_relative 'r66_t32_pair_bounds'
class TestR66T32PairBounds < Minitest::Test
  B=RithmT32::PairBounds;C=B::C
  def test_moments_and_dynamic_bounds
    rng=Random.new(3203)
    100.times do
      w=Array.new(6){rng.rand(1..20)};q=w.map{|x|Rational(x,w.sum)}
      p=q.each_with_index.sum{|x,k|x*k}/5r;t=q.each_with_index.sum{|x,k|x*k*(k-1)}/20r
      l=[0,t-1r/100].max;h=[p,t+1r/100].min
      vs=B.vertices(p,l,h)
      vs.each do |v|
        assert_equal 1,v.sum;assert v.all?{|x|x>=0};assert_equal 5*p,v.each_with_index.sum{|x,k|x*k}
        assert v.each_with_index.sum{|x,k|x*k*(k-1)}.between?(20*l,20*h)
      end
      n=rng.rand(1..20);r=B.bounds(p,l,h,n);v=C.absorbing_cost(q,n)
      assert_operator v,:>=,r[:lower];assert_operator v,:<=,r[:upper]
      [:lower,:upper].each do |s|
        v=3;r.fetch(:"#{s}_laws").each_with_index{|law,i|v=B.step(law,v,i+1)};assert_equal r[s],v
      end
    end
  end
  def test_pairwise_independence_does_not_fix_dynamic_cost
    p=7r/160;t=p*p;r=B.bounds(p,t,t,40);ind=C.absorbing_cost(C.independent([p]*5),40)
    assert_operator r[:lower],:<,ind;assert_operator r[:upper],:>,ind
    base=C.absorbing_cost(C.independent([7r/200]*5),40)
    lo=[2049r/2560,231r/1280,49r/2560,0,0,0]
    hi=[5049r/6400,1071r/5120,0,0,0,49r/25600]
    [lo,hi].each do |q|
      assert_equal 1,q.sum;assert_equal 5*p,q.each_with_index.sum{|v,k|v*k}
      assert_equal 20*t,q.each_with_index.sum{|v,k|v*k*(k-1)}
    end
    assert_equal C.absorbing_cost(lo,40),r[:lower]
    assert_equal C.absorbing_cost(hi,40),r[:upper]
    assert_operator r[:lower],:<,base;assert_operator r[:upper],:>,base
    assert_equal 3,B.bounds(0,0,0,1)[:upper]
    assert_raises(ArgumentError){B.vertices(1r/2,0,0)}
    assert_raises(ArgumentError){B.bounds(p,t,t,0)}
  end
end
