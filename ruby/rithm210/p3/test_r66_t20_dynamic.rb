require 'minitest/autorun'
require_relative 'r66_t20_dynamic'
require_relative 'r66_t19_equilibrium'
class TestR66T20 < Minitest::Test
  D=RithmT20::Dynamic
  def test_n5_matches_t19
    (0..100).each do |i|
      k=Rational(i,50)
      assert_equal RithmT19::Equilibrium.equilibria(k).values.uniq.sort,D.symmetric(5,k).sort
    end
  end
  def test_all_states_mass_and_equilibrium
    (0..6).each do |n|
      [0,Rational(1,4),Rational(4,9),Rational(1,2),Rational(3,4),1,Rational(5,4),2].each do |k|
        assert D.pure(n,k).size>0
        D.symmetric(n,k).each do |a,b|
          ga,gb=D.gains(n,a,b,k)
          assert D.br?(a,ga) if n>0
          assert D.br?(b,gb) if n<6
          row,s=D.mixed_row(n,a,b)
          assert_equal 1,row.sum
          assert_equal n*a+(6-n)*b,s
        end
      end
    end
  end
  def test_two_period_bound_against_t19
    r=D.bounds(horizon:2,kappa:0)
    assert_equal Rational(9,2),r[:lo][5]
    assert_equal Rational(13,2),r[:hi][5]
    r=D.bounds(horizon:2,kappa:Rational(1,2))
    assert_equal Rational(9,2),r[:lo][5]
    assert_equal Rational(9,2)+Rational(119,96),r[:hi][5]
  end
  def test_efficient_state_stability_boundary
    assert_operator D.symmetric(4,Rational(4,7)).size,:>,1
    [Rational(3,5),Rational(3,4),Rational(99,100)].each do |k|
      assert_equal [[0,0]],D.symmetric(4,k)
      assert_equal [4],D.actions(4,k).map { |row,s| row.index(1) }.uniq
      r=D.bounds(horizon:40,kappa:k,resource:k)
      assert_equal 0,r[:lo][4]
      assert_equal 78*k,r[:hi][4]
    end
  end
  def test_no_opportunity_and_horizon_one
    r=D.bounds(horizon:40,kappa:Rational(1,2),opportunity:0)
    assert_equal (0..6).map { |n| 120*(n-4)**2 },r[:lo]
    assert_equal r[:lo],r[:hi]
    r=D.bounds(horizon:1,kappa:0,resource:100)
    assert_equal (0..6).map { |n| 3*(n-4)**2 },r[:lo]
  end
end
