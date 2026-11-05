require 'minitest/autorun'
require_relative 'shock_afterlife'
class TestRithm210ShockAfterlife < Minitest::Test
  M=Rithm210ShockAfterlife
  def test_exact_rational_discounted_welfare
    b=Rational(9,10)
    assert_equal Rational(5025,19),M.discounted_sync(post_shock_n:3,beta:b)
    assert_equal Rational(5349,19),M.discounted_sync(post_shock_n:5,beta:b)
    assert_equal Rational(60,11),M.discounted_async_random_actor(post_shock_n:3,beta:b)
    assert_equal Rational(60,17),M.discounted_async_random_actor(post_shock_n:5,beta:b)
  end
  def test_beta_zero_and_post_shock_dynamics
    [3,5].each do |n|
      assert_equal 3,M.discounted_sync(post_shock_n:n,beta:0)
      assert_equal 3,M.discounted_async_random_actor(post_shock_n:n,beta:0)
      assert_equal(n==3 ? 6 : 0,M.example.fetch(n)[:first_synchronous])
    end
  end
  def test_synchronized_welfare_diverges_as_discount_to_one
    a=[Rational(9,10),Rational(99,100),Rational(999,1000)].map do |b|
      [M.discounted_sync(post_shock_n:3,beta:b),
       M.discounted_async_random_actor(post_shock_n:3,beta:b)]
    end
    assert_operator a[2][0],:>,a[1][0]
    assert_operator a[1][0],:>,a[0][0]
    assert_operator a[2][1],:<,6
  end
  def test_invalid_domain
    assert_raises(ArgumentError){M.discounted_sync(post_shock_n:4,beta:0.5)}
    assert_raises(ArgumentError){M.discounted_sync(post_shock_n:3,beta:1)}
  end
end
