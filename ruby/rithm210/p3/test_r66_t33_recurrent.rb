require 'minitest/autorun'
require_relative 'r66_t33_recurrent'
class TestR66T33Recurrent < Minitest::Test
  R=RithmT33::Recurrent
  def test_absorbing_limit_and_recovery
    p=7r/160;t=p*p;q=R::C.independent([p]*5)
    assert_equal R::C.absorbing_cost(q,40),R.finite(q,0,40)
    b=R::B.bounds(p,t,t,40);assert_equal [b[:lower],b[:upper]],R.bounds(p,t,0,40)
    old=R::C.independent([7r/200]*5)
    assert_operator R.bounds(p,t,1r/100,40).last,:>,R.finite(old,1r/100,40)
    assert_operator R.bounds(p,t,1r/20,40).last,:<,R.finite(old,1r/20,40)
    assert_operator R.stationary_bounds(p,t,1r/20).last,:>,R.stationary(old,1r/20)
  end
  def test_against_forward_propagation_and_stationary_law
    rng=Random.new(3301)
    60.times do
      w=Array.new(6){rng.rand(1..20)};q=w.map{|x|Rational(x,w.sum)};r=Rational(rng.rand(1..10),10);h=rng.rand(1..20)
      state=[1,0,0,0,0,0];cost=0
      h.times do
        cost+=state.zip(R::COST).sum{|a,b|a*b}
        state=[state[0]*q[0]+r*state.drop(1).sum,*(1..5).map{|m|state[0]*q[m]+(1-r)*state[m]}]
      end
      assert_equal cost,R.finite(q,r,h)
      p=q.each_with_index.sum{|x,k|x*k}/5r;t=q.each_with_index.sum{|x,k|x*k*(k-1)}/20r
      lo,hi=R.bounds(p,t,r,h);assert cost.between?(lo,hi)
      s=R.stationary(q,r);den=r+1-q[0];pi=[r/den,*q.drop(1).map{|x|x/den}]
      assert_equal 1,pi.sum;assert_equal s,pi.zip(R::COST).sum{|a,b|a*b}
      assert s.between?(*R.stationary_bounds(p,t,r))
    end
  end
  def test_guards
    assert_raises(ArgumentError){R.finite([1]*6,0,2)}
    assert_raises(ArgumentError){R.stationary([1,0,0,0,0,0],0)}
    assert_raises(ArgumentError){R.bounds(0,0,2,2)}
  end
end
