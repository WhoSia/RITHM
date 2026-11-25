require 'minitest/autorun'
require_relative 'r66_t25_two_proxy'
require_relative 'r66_t24_welfare'
class TestR66T25TwoProxy < Minitest::Test
  T=RithmT25::TwoProxy;W=RithmT24::Welfare
  def test_exact_recovery
    rng=Random.new(2501)
    300.times do
      q=Rational(rng.rand(1..9),10);p=Rational(rng.rand(1..10),10)
      a1,b1=(0..10).to_a.sample(2,random:rng).map{|x|Rational(x,10)};a2,b2=(0..10).to_a.sample(2,random:rng).map{|x|Rational(x,10)}
      j=T.joint(q,p,T.product(a1,a2),T.product(b1,b2));w=T.identify(*j)
      assert_equal :point,w[:status];assert_equal q,w[:q];assert_equal p,w[:response];assert_equal j,T.joint(*w.values_at(:q,:response,:active,:inactive))
    end
  end
  def test_dependence_restores_opposite_policy_welfare
    s=Rational(7,200);q=Rational(4,5);a=T.product(Rational(4,5),Rational(4,5));b=T.product(Rational(3,10),Rational(3,10));j=T.joint(q,s/q,a,b)
    w=T.identify(*j);assert_equal q,w[:q]
    rival=T.witness(*j,Rational(1,2));assert_equal Rational(3,50),rival[:inactive_covariance]
    assert_equal j,T.joint(*rival.values_at(:q,:response,:active,:inactive))
    base=W.values(W.cognitive(s),40)[5]
    assert_operator W.values(W.cognitive(w[:response]),40)[5],:<,base
    assert_operator W.values(W.cognitive(rival[:response]),40)[5],:>,base
  end
  def test_degeneracy_and_invalid
    a=T.product(Rational(1,2),Rational(2,3));j=T.joint(Rational(1,2),Rational(1,2),a,a)
    assert_equal({status: :set,q_low:Rational(1,4),q_high:1},T.identify(*j))
    j=T.joint(1,Rational(1,2),[Rational(1,2),0,0,Rational(1,2)],a)
    assert_raises(ArgumentError){T.identify(*j)}
    assert_raises(ArgumentError){T.identify(a,[0]*4)}
  end
end
