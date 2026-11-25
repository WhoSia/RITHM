require 'minitest/autorun'
require_relative 'r66_t23_monotone_proxy'
class TestR66T23MonotoneProxy < Minitest::Test
  M=RithmT23::MonotoneProxy;I=RithmT22::Identification
  def joint(a,b,q,alpha,beta)
    [0,1].map{|z|a.zip(b).map{|x,y|q*x*(z==1 ? alpha : 1-alpha)+(1-q)*y*(z==1 ? beta : 1-beta)}}
  end
  def witness(j,w)
    assert_equal j,joint(*w.values_at(:active,:inactive,:q,:alpha,:beta))
    assert_operator w[:alpha],:>=,w[:beta];assert_operator w[:q],:>,0
    [:active,:inactive].each{|k|assert_equal 1,w[k].sum;assert w[k].all?{|v|v>=0}}
  end
  def test_arbitrary_drift_and_sharp_binary_example
    a=[0,0,0,1,0,0];b=[0,0,0,0,0,1];j=joint(a,b,Rational(1,2),Rational(9,10),Rational(1,10))
    x=M.bounds(*j,:b);assert_equal [Rational(7,5),2],x.values_at(:low,:high)
    witness(j,x[:low_witness]);witness(j,x[:high_witness])
    assert_equal Rational(1,10),1-x[:low_witness][:inactive][5]
  end
  def test_random_monotone_independent_measurement
    rng=Random.new(2304)
    300.times do
      a,b=Array.new(2){w=Array.new(6){rng.rand(1..9)};w.map{|x|Rational(x,w.sum)}}
      q=Rational(rng.rand(1..10),10);beta,alpha=Array.new(2){Rational(rng.rand(0..10),10)}.sort
      j=joint(a,b,q,alpha,beta)
      [:a,:b].each do |route|
        x=M.bounds(*j,route);g=I.gain(a,route);assert_operator g,:>=,x[:low];assert_operator g,:<=,x[:high]
        witness(j,x[:low_witness]);witness(j,x[:high_witness])
      end
    end
  end
  def test_zero_covariance_and_reversed_proxy_counterexample
    a=[0,0,0,1,0,0];b=[0,0,0,0,0,1];q=Rational(1,2)
    j=joint(a,b,q,Rational(1,2),Rational(1,2));x=M.bounds(*j,:b);assert_equal [-4,2],x.values_at(:low,:high);witness(j,x[:low_witness]);witness(j,x[:high_witness])
    j=joint(a,b,q,Rational(9,10),Rational(1,10))
    assert_equal j,joint(b,a,q,Rational(1,10),Rational(9,10));assert_equal(-4,I.gain(b,:b))
    assert_raises(ArgumentError){M.bounds([0]*6,[0]*6,:b)}
  end
end
