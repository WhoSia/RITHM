require 'minitest/autorun'
require_relative 'r66_t22_proxy'
class TestR66T22Proxy < Minitest::Test
  P=RithmT22::Proxy;I=RithmT22::Identification
  def delta(k);Array.new(6){|j|j==k ? 1 : 0};end
  def test_proxy_resolves_sign_without_known_false_positive
    a,b=P.joint(5,delta(3),Rational(1,2),Rational(9,10),Rational(1,10))
    x=P.bounds(5,a,b,:b)
    assert_equal Rational(9,10),x[:sensitivity];assert_equal Rational(5,9),x[:q_high]
    assert_equal Rational(7,5),x[:low];assert_equal 2,x[:high]
    y=P.bounds(5,a,b,:b,false_positive:Rational(1,10));assert_equal 2,y[:low];assert_equal 2,y[:high]
  end
  def test_exact_feasibility_and_sharpness
    (0..5).to_a.permutation(2).each do |k,j|
      [Rational(1,4),Rational(1,2),1].product([0,Rational(1,2),1],[0,Rational(1,2),1]).each do |q,alpha,beta|
        active=I.mix(k,delta(j),Rational(1,2));a,b=P.joint(k,active,q,alpha,beta)
        x=P.bounds(k,a,b,:a);g=I.gain(active,:a);assert_operator g,:>=,x[:low];assert_operator g,:<=,x[:high]
        [x[:q_low],x[:q_high]].each do |v|
          p=a.zip(b).map(&:sum);z=v==1 ? 0 : (b.sum-alpha*v)/(1-v)
          assert_equal [a,b],P.joint(k,I.recover(k,p,v),v,alpha,z)
        end
        next if alpha==beta
        x=P.bounds(k,a,b,:a,false_positive:beta);assert_equal q,x[:q_low];assert_equal q,x[:q_high]
      end
    end
  end
  def test_falsifiable_proxy_assumption
    assert_raises(ArgumentError){P.bounds(5,[0,0,Rational(1,4),0,0,Rational(1,4)],[0,0,0,Rational(1,4),0,Rational(1,4)],:a)}
    assert_raises(ArgumentError){P.bounds(5,delta(5),[0]*6,:a)}
  end
end
