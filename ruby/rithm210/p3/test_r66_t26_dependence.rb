require 'minitest/autorun'
require_relative 'r66_t26_dependence'
class TestR66T26Dependence < Minitest::Test
  D=RithmT26::Dependence;T=RithmT25::TwoProxy
  def fixture
    T.joint(Rational(4,5),Rational(7,160),T.product(Rational(4,5),Rational(4,5)),T.product(Rational(3,10),Rational(3,10)))
  end
  def test_disconnected_and_exact_point
    j=fixture;d=Rational(1,20);c=D.cover(*j,delta:d)
    assert D.feasible?(*j,Rational(7,200),delta:d)
    refute D.feasible?(*j,Rational(3,5),delta:d)
    assert D.feasible?(*j,Rational(4,5),delta:d)
    assert c.each_cons(2).any?{|a,b|a[1]<b[0]}
    z=D.cover(*j,delta:0);assert z.any?{|a,b,_|Rational(4,5).between?(a,b)}
    assert z.all?{|a,b,_|b-a<=Rational(2,100_000)}
  end
  def test_rational_grid_against_constructive_witness
    j=fixture
    [0,Rational(1,25),Rational(1,20),Rational(3,50),Rational(1,4)].each do |d|
      c=D.cover(*j,delta:d)
      (35..828).each do |i|
        q=Rational(i,1000);w=T.witness(*j,q);f=w[:inactive_covariance].abs<=d
        assert_equal f,D.feasible?(*j,q,delta:d)
        assert c.any?{|a,b,_|q.between?(a,b)} if f
        assert f if c.any?{|a,b,s|s==:inside && q.between?(a,b)}
      end
    end
  end
  def test_degenerate_and_null_inactive_class
    a=T.product(Rational(1,3),Rational(2,3));j=T.joint(1,Rational(1,2),a,a)
    assert_equal [[Rational(1,2),1,:inside]],D.cover(*j,delta:0)
    a=[Rational(1,2),0,0,Rational(1,2)];j=T.joint(1,Rational(1,2),a,a)
    assert D.feasible?(*j,1,delta:0);refute D.feasible?(*j,Rational(9,10),delta:0)
    assert_raises(ArgumentError){D.cover(*j,delta:-1)}
  end
end
