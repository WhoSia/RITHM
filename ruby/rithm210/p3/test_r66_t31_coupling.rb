require 'minitest/autorun'
require_relative 'r66_t31_coupling'
class TestR66T31Coupling < Minitest::Test
  C=RithmT31::Coupling
  def test_exact_marginal_and_extremal_witnesses
    rng=Random.new(3101)
    300.times do
      p=Array.new(rng.rand(1..6)){Rational(rng.rand(0..20),20)}
      target=rng.rand(0..6);lo,hi=C.bounds(p,target:target)
      [C.lower(p),C.upper(p)].zip([lo,hi]).each do |law,cost|
        assert_equal 1,law.values.sum
        assert law.keys.all?{|b|b.all?{|x|[0,1].include?(x)}}
        p.each_index{|i|assert_equal p[i],law.sum{|b,w|b[i]*w}}
        assert_equal cost,law.sum{|b,w|w*3*(b.sum-target)**2}
      end
      independent=C.independent(p).each_with_index.sum{|w,n|w*3*(n-target)**2}
      assert_operator independent,:>=,lo;assert_operator independent,:<=,hi
    end
  end
  def test_policy_reversal_same_marginals
    s=7r/200;p=7r/160;base=C.absorbing_cost(C.independent([s]*5),40)
    low=C.absorbing_cost(C.occupancy(C.lower([p]*5),5),40)
    high=C.absorbing_cost(C.occupancy(C.upper([p]*5),5),40)
    assert_operator low,:<,base;assert_operator high,:>,base
    assert_operator C.absorbing_cost(C.independent([p]*5),40),:<,base
  end
  def test_guards
    assert_raises(ArgumentError){C.bounds([])}
    assert_raises(ArgumentError){C.lower([-1])}
    assert_raises(ArgumentError){C.absorbing_cost([1]*6,40)}
  end
end
