require 'minitest/autorun'
require_relative 'r66_t22_sensitivity'
require_relative 'r66_t22_proxy'
class TestR66T22Sensitivity < Minitest::Test
  S=RithmT22::Sensitivity;P=RithmT22::Proxy;I=RithmT22::Identification
  def delta(k);Array.new(6){|j|j==k ? 1 : 0};end
  def test_sign_robustness_and_no_information_limit
    a,b=P.joint(5,delta(3),Rational(1,2),Rational(9,10),Rational(1,10))
    assert_equal Rational(7,5),S.bounds(5,a,b,:b,delta:0)[:low]
    assert_equal 0,S.bounds(5,a,b,:b,delta:Rational(7,10))[:low]
    assert_operator S.bounds(5,a,b,:b,delta:Rational(69,100))[:low],:>,0
    assert_operator S.bounds(5,a,b,:b,delta:Rational(71,100))[:low],:<,0
    assert_equal(-1,S.bounds(5,a,b,:b,delta:1)[:low])
  end
  def test_sharp_endpoint_witnesses
    (0..5).to_a.permutation(2).each do |k,j|
      [Rational(1,3),Rational(2,3),1].product([0,Rational(1,2),1],[0,Rational(1,2),1]).each do |q,alpha,beta|
        active=I.mix(k,delta(j),Rational(1,2));a,b=P.joint(k,active,q,alpha,beta)
        [0,Rational(1,4),1].each do |d|
          x=S.bounds(k,a,b,:a,delta:d);assert_operator q,:>=,x[:q_low];assert_operator q,:<=,x[:q_high]
          [x[:q_low],x[:q_high]].each do |v|
            w=S.witness(k,a,b,v,delta:d);u=w[:active_untagged];t=w[:active_tagged];z=w[:inactive_tagged];y=w[:inactive_untagged]
            assert (u+t+[z,y]).all?{|m|m>=0};assert_equal v,u.sum+t.sum;assert_equal 1-v,z+y
            assert_equal a,u.each_with_index.map{|m,i|m+(i==k ? y : 0)};assert_equal b,t.each_with_index.map{|m,i|m+(i==k ? z : 0)}
            if u[k]+t[k]>0
              assert_operator (t[k]/(u[k]+t[k])-x[:alpha_mover]).abs,:<=,d
            end
          end
        end
      end
    end
  end
  def test_differential_off_diagonal_allowed
    a=[0,0,Rational(1,4),0,0,Rational(1,4)];b=[0,0,0,Rational(1,4),0,Rational(1,4)]
    assert_equal Rational(1,2),S.bounds(5,a,b,:b,delta:0)[:alpha_mover]
    assert_raises(ArgumentError){P.bounds(5,a,b,:b)}
  end
end
