require 'minitest/autorun'
require_relative 'r66_t19_equilibrium'
class TestR66T19Equilibrium < Minitest::Test
  E=RithmT19::Equilibrium
  def test_zero_friction_branches
    assert_equal({low:[Rational(1,12),0],high:[Rational(1,3),1],interior:[Rational(4,15),Rational(11,15)]},E.equilibria(0))
    assert_equal [Rational(13,6),Rational(11,3),4],E.equilibria(0).values.map { |a,b| E.congestion(a,b) }
    assert_equal 15,E.pure(0).size
    assert_equal [4],E.pure(0).map { |x| x[:n] }.uniq
  end
  def test_friction_removes_high_cost_mixed_branches
    assert_equal 3,E.equilibria(Rational(4,9)).size
    assert_equal 2,E.equilibria(Rational(4,9)).values.uniq.size
    assert_equal [:low],E.equilibria(Rational(1,2)).keys
    assert_equal 15,E.pure(Rational(1,2)).size
    assert_equal [4,5],E.pure(1).map { |x| x[:n] }.uniq.sort
    assert_equal [5],E.pure(Rational(11,10)).map { |x| x[:n] }.uniq
    100.times do |i|
      k=Rational(i,100); branches=E.equilibria(k)
      assert_operator E.congestion(*branches[:low]),:<,3
      [:high,:interior].each { |m| assert_operator E.congestion(*branches[m]),:>,3 if branches[m] }
    end
  end
  def test_real_resource_cost_boundary
    [0,Rational(1,2),Rational(99,100)].each do |k|
      a,b=E.equilibria(k)[:low]
      assert_equal 3,E.resource_cost(a,b,2+k)
      assert_operator E.resource_cost(a,b,2+k-Rational(1,100)),:<,3
      assert_operator E.resource_cost(a,b,2+k+Rational(1,100)),:>,3
      assert_equal({1=>5,3=>10},E.pure(k).group_by { |x| x[:switches] }.transform_values(&:size))
    end
  end
  def test_independent_mask_enumeration
    [0,Rational(1,4),Rational(4,9),Rational(1,2),1].each do |k|
      E.equilibria(k).values.each do |a,b|
        mass=0;cost=0
        64.times do |mask|
          n=5;p=1
          6.times do |i|
            r=i<5 ? a : b
            if mask[i]==1
              p*=r;n+=i<5 ? -1 : 1
            else
              p*=1-r
            end
          end
          mass+=p;cost+=p*3*(n-4)**2
        end
        assert_equal 1,mass;assert_equal E.congestion(a,b),cost
      end
    end
  end
end
