require 'minitest/autorun'
require_relative 'r66_t37_regret'
class TestR66T37Regret < Minitest::Test
  R=RithmT37::Regret
  def test_exact_no_information_and_separation
    assert_equal 6r/5,R.solve([1r],[1r],2r,3r)[:risk]
    assert_equal 0,R.solve([1r,0r],[0r,1r],2r,3r)[:risk]
    assert_equal 1,R.solve([3r/4,1r/4],[1r/4,3r/4],4r,4r)[:risk]
  end
  def test_binomial_and_randomized_oracle
    rng=Random.new(3702)
    20.times do
      p=rng.rand(0..10)/10r;q=rng.rand(0..10)/10r;a=R.binomial(p,3);b=R.binomial(q,3)
      assert_equal 1,a.sum;assert_equal 1,b.sum
      s=R.solve(a,b,2r,3r);f=s[:policy]
      assert_equal s[:world_a],2*a.zip(f).sum{|x,y|x*(1-y)}
      assert_equal s[:world_b],3*b.zip(f).sum{|x,y|x*y}
      [0r,1r/4,1r/2,3r/4,1r].repeated_permutation(4) do |v|
        assert_operator s[:risk],:<=,[2*a.zip(v).sum{|x,y|x*(1-y)},3*b.zip(v).sum{|x,y|x*y}].max
      end
    end
  end
  def test_more_data_cannot_hurt
    z=R.audit;z[:events].each_value do |v|
      a=[z[:no_data],*v[:risks].values];assert a.each_cons(2).all?{|x,y|y<=x+1e-12}
    end
    assert_equal z[:events]['no_switch'][:risks],z[:events]['any_switch'][:risks]
  end
end
