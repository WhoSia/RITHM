require 'minitest/autorun'
require_relative 'r66_t23_drift'
class TestR66T23Drift < Minitest::Test
  D=RithmT23::Drift;I=RithmT22::Identification
  def delta(k);Array.new(6){|j|j==k ? 1 : 0};end
  def check_witness(k,p,e,w)
    q=w[:q];a=w[:active];b=w[:inactive]
    assert_equal 1,a.sum;assert_equal 1,b.sum;assert (a+b).all?{|x|x>=0}
    assert_operator 1-b[k],:<=,e
    assert_equal p,a.zip(b).map{|x,y|q*x+(1-q)*y}
  end
  def test_exact_reduces_to_t22
    (0..5).to_a.permutation(2).each do |k,j|
      (1..9).each do |m|
        q=Rational(m,10);p=I.mix(k,delta(j),q)
        [:a,:b].each do |route|
          x=D.bounds(k,p,route,eps:0,q_min:Rational(1,100));y=I.bounds(k,p,route)
          assert_equal y[:low],x[:low][:gain];assert_equal y[:high],x[:high][:gain]
        end
      end
    end
  end
  def test_drift_and_cross_row_boundary
    p=I.mix(5,delta(3),Rational(1,2))
    x=D.bounds(5,p,:b,eps:Rational(7,24),q_min:Rational(1,2),q_max:Rational(5,9))
    assert_equal 0,x[:low][:gain];assert_equal 2,x[:high][:gain]
    check_witness(5,p,Rational(7,24),x[:low]);check_witness(5,p,Rational(7,24),x[:high])
    other=I.mix(0,delta(1),Rational(4,5));rows=(0..5).map{|k|delta(k)};rows[0]=other;rows[5]=p
    q=D.shared_minimum(rows,Rational(1,10));assert_equal Rational(7,9),q
    assert_equal Rational(-1,7),D.bounds(5,p,:b,eps:Rational(1,10),q_min:q)[:high][:gain]
    assert_equal Rational(3,4),D.shared_minimum(rows,Rational(1,5))
  end
  def test_random_rational_witness_and_grid_containment
    rng=Random.new(2301)
    100.times do
      k=rng.rand(6);w=Array.new(6){rng.rand(1..9)};p=w.map{|x|Rational(x,w.sum)};e=Rational(rng.rand(0..10),10)
      [:a,:b].each do |route|
        x=D.bounds(k,p,route,eps:e,q_min:Rational(1,10));check_witness(k,p,e,x[:low]);check_witness(k,p,e,x[:high])
        11.times do |j|
          q=x[:q_low]+(x[:q_high]-x[:q_low])*Rational(j,10)
          [-1,1].each do |s|
            y=D.at(k,p,1/q,e,route,s);assert_operator y[:gain],:>=,x[:low][:gain];assert_operator y[:gain],:<=,x[:high][:gain]
          end
        end
      end
    end
  end
  def test_guards
    assert_raises(ArgumentError){D.bounds(5,delta(3),:a,eps:0,q_min:Rational(1,2),q_max:Rational(3,4))}
    assert_raises(ArgumentError){D.bounds(5,delta(5),:a,eps:1,q_min:0)}
  end
end
