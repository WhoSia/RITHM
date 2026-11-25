require 'minitest/autorun'
require_relative 'r66_t26_policy'
class TestR66T26Policy < Minitest::Test
  P=RithmT26::Policy;D=RithmT26::Dependence;T=RithmT25::TwoProxy;W=RithmT24::Welfare
  def fixture
    T.joint(4r/5,7r/160,T.product(4r/5,4r/5),T.product(3r/10,3r/10))
  end
  def test_closed_form_and_range_against_dp
    [1,2,5,12,40].each do |h|
      (0..20).each do |i|
        p=Rational(i,20);assert_equal W.values(W.cognitive(p),h)[5],P.cost(p,h)
        lo,hi=P.cost_range(p,p,h);assert_equal lo,hi;assert_equal lo,P.cost(p,h)
      end
      (0...10).each do |i|
        l=Rational(i,10);u=l+1r/10;lo,hi=P.cost_range(l,u,h)
        (0..10).each do |j|
          v=P.cost(l+(u-l)*Rational(j,10),h);assert_operator v,:>=,lo;assert_operator v,:<=,hi
        end
      end
    end
  end
  def test_critical_dependence_threshold_and_positive_gain_rival
    j=fixture;s=7r/200;d=T.witness(*j,s)[:inactive_covariance]
    # Covariance on [s,.7] is >= its value at s; derivative changes sign only at .6.
    assert_equal 1530r/37249,d
    assert P.certify(s,[[7r/10,53r/64,:inside]])[:improvement_certified]
    assert P.certify(s,D.cover(*j,delta:1r/25))[:improvement_certified]
    assert D.feasible?(*j,s,delta:d);assert_operator P.cost(1,40),:>,P.cost(s,40)
    assert D.feasible?(*j,1r/2,delta:3r/50);assert_operator W.active_gain(7r/100).first,:>,0
    assert_operator P.cost(7r/100,40),:>,P.cost(s,40)
  end
  def test_inconclusive_is_not_success
    refute P.certify(7r/200,[])[:improvement_certified]
    refute P.certify(7r/200,[[1,1,:inside]])[:improvement_certified]
    assert_raises(ArgumentError){P.cost_range(0,2,40)}
  end
end
