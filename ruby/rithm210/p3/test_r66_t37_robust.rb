require 'minitest/autorun'
require_relative 'r66_t37_robust'
class TestR66T37Robust < Minitest::Test
  R=RithmT37::Robust;S=R::S
  def test_against_all_two_state_row_policies
    f=[[[1,0],[0,1]],[[1r/2,1r/2],[0,1]]];c=[1,3]
    ps=f[0].product(f[1]).map{|x|x}
    (1..6).each{|h|assert_equal S.rectangular(ps,c,h),R.bounds(f,c,h)}
  end
  def test_exact_moments_and_nested_bounds
    rng=Random.new(3701)
    10.times do
      p=Array.new(7){w=Array.new(7){rng.rand(1..10)};w.map{|x|Rational(x,w.sum)}}
      base=R.fibers(p,'none');a,b=R.bounds(base,R::C,5);v=S.values(p,R::C,5)
      assert_equal [S.values(p,R::C,2)]*2,R.bounds(base,R::C,2)
      R::NAMES.drop(1).each do |name|
        lo,hi=R.bounds(R.fibers(p,name),R::C,5)
        7.times{|i|assert a[i]<=lo[i] && lo[i]<=v[i] && v[i]<=hi[i] && hi[i]<=b[i]}
      end
    end
    assert_raises(ArgumentError){R.bounds([[]],[1],2)}
  end
end
