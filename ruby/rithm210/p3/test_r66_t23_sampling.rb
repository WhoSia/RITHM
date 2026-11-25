require 'minitest/autorun'
require_relative 'r66_t23_sampling'
class TestR66T23Sampling < Minitest::Test
  S=RithmT23::Sampling
  def test_known_q_and_shrinking_interval
    prev=nil
    [100,1000,10000,100000].each do |n|
      x=S.bounds(5,[0,0,0,n/2,0,n/2],:b,eps:0,q_min:0.5,q_max:5.0/9)
      assert_operator x[:low],:<=,1.4;assert_operator x[:high],:>=,2
      assert_operator x[:high]-x[:low],:<=,prev if prev
      prev=x[:high]-x[:low]
    end
  end
  def test_zero_lower_bound_and_incompatible
    x=S.bounds(5,[0,0,0,0,0,10],:b,eps:0.2,q_min:0)
    assert_equal [-4,11],[x[:low],x[:high]]
    assert_equal :incompatible,S.bounds(5,[0,0,0,10000,0,0],:b,eps:0,q_min:0,q_max:0.5)[:status]
    assert_raises(ArgumentError){S.bounds(5,[0]*6,:a,eps:0,q_min:0)}
  end
  def test_exact_binomial_coverage_on_independent_binary_rows
    # True q=1/2, A=delta3, B=delta5. Binomial count is sufficient.
    n=40;[0.01,0.05,0.1].each do |alpha|
      missed=0;coef=1
      (0..n).each do |x|
        b=S.bounds(5,[0,0,0,x,0,n-x],:b,eps:0,q_min:0.5,q_max:5.0/9,alpha:alpha)
        missed+=coef if b[:status]!=:ok || b[:low]>2 || b[:high]<2
        coef=coef*(n-x)/(x+1)
      end
      assert_operator Rational(missed,2**n),:<=,alpha
    end
  end
end
