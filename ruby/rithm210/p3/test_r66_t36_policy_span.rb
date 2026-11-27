require 'minitest/autorun'
require_relative 'r66_t36_policy_span'
class TestR66T36PolicySpan < Minitest::Test
  P=RithmT36::PolicySpan;S=P::S
  def kernel(dest)
    dest.map{|j|Array.new(dest.size){|i|i==j ? 1 : 0}}
  end
  def test_constant_policy_does_not_imply_schedule_equivalence
    c=[0,0,0,1];a=kernel([1,0,0,3]);alt=kernel([2,0,0,3]);b=kernel([0,3,2,3])
    assert P.equivalent?([a],[alt],c);assert P.equivalent?([b],[b],c)
    refute P.equivalent?([a,b],[alt,b],c)
    assert_equal 1,P.schedule([a,b],c,[0,1])[0];assert_equal 0,P.schedule([alt,b],c,[0,1])[0]
  end
  def test_open_loop_does_not_imply_feedback_equivalence
    c=[0,0,0,1];a=kernel([1,0,0,3]);alt=kernel([2,0,0,3]);b=kernel([0,3,3,3])
    assert P.equivalent?([a,b],[alt,b],c)
    refute P.equivalent?([a,b],[alt,b],c,feedback:true)
    assert_equal [2,3],P.profile([a,b],c)[:ranks]
    assert_equal 4,P.profile([a,b],c,feedback:true)[:basis].size
    f=[a[0],b[1],a[2],a[3]]
    assert_equal 1,P.schedule([a,f],c,[0,1])[0];assert_equal 0,P.schedule([alt,f],c,[0,1])[0]
  end
  def test_feedback_generators_span_all_small_policies
    rng=Random.new(3601)
    30.times do
      n=4;ps=3.times.map{kernel(Array.new(n){rng.rand(n)})};c=Array.new(n){rng.rand(3)}
      b=P.profile(ps,c,feedback:true)[:basis]
      [0,1,2].repeated_permutation(n) do |acts|
        q=acts.each_with_index.map{|a,i|ps[a][i]}
        assert_equal 0,S.deficit(b,b.map{|v|S.apply(q,v)})
      end
    end
  end
  def test_fiber_against_masks
    64.times do |x|
      64.times do |y|
        a=x.digits(2).sum;b=y.digits(2).sum;g=(x^y).digits(2).sum;lo,hi=P.fiber(a,b)
        assert g.between?(lo,hi)&&(g-lo).even?
      end
    end
    assert_equal [0,4],P.fiber(4,4)
  end
end
