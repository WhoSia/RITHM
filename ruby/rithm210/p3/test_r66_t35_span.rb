require 'minitest/autorun'
require_relative 'r66_t35_span'
require_relative 'r66_t33_recurrent'
class TestR66T35Span < Minitest::Test
  S=RithmT35::Span;R=RithmT33::Recurrent
  def reset(q,r)
    [q,*(1..5).map{|m|Array.new(6){|i|i==0 ? r : i==m ? 1-r : 0}}]
  end
  def test_reset_one_extra_measurement
    p=7r/160;q=R::C.independent([p]*5);base=reset(q,1r/20);c=R::COST
    obs=[Array.new(6,1),(0..5).to_a,(0..5).map{|m|m*(m-1)}];z=[1,0,0,0,0,0]
    b=S.basis(base,c);assert_equal 1,S.deficit(obs,b);assert_equal 0,S.deficit(obs+[z],b)
    assert_equal 1,S.additions(obs,b).size
    vs=R::B.vertices(p,p*p,p*p);assert vs.any?{|a|!S.equivalent?(base,reset(a,1r/20),c)}
    # Equal q0 and moments, different higher count probabilities.
    d=[0,1,-3,3,-1,0];e=1r/1000000;alt=q.zip(d).map{|x,y|x+e*y}
    assert alt.all?{|x|x>=0};assert_equal S.apply(obs,q),S.apply(obs,alt)
    assert S.equivalent?(base,reset(alt,1r/20),c)
    [1,2,3,10,40].each{|h|assert_equal S.values(base,c,h),S.values(reset(alt,1r/20),c,h);assert_equal [S.values(base,c,h)]*2,S.rectangular([base,reset(alt,1r/20)],c,h)}
  end
  def test_fixed_law_vs_rectangular
    c=[0,1,3];a=[[0,1,0],[0,0,1],[1,0,0]];b=[[0,0,1],[0,0,1],[1,0,0]]
    assert_equal 7,S.rectangular([a,b],c,5).last.first
    (0..20).each do |i|
      p=i/20r;q=[[0,1-p,p],a[1],a[2]]
      assert_equal 5+4*p-3*p*p,S.values(q,c,5).first
    end
    p=2r/3;assert_equal 19r/3,S.values([[0,1-p,p],a[1],a[2]],c,5).first
    refute S.equivalent?(a,b,c)
  end
  def test_basis_closure_random
    rng=Random.new(3501)
    50.times do
      n=rng.rand(2..7);p=Array.new(n){w=Array.new(n){rng.rand(1..8)};w.map{|x|Rational(x,w.sum)}};c=Array.new(n){rng.rand(0..10)}
      b=S.basis(p,c);assert_equal b.size,S.rank(b);assert_equal 0,S.deficit(b,b.map{|x|S.apply(p,x)})
      assert S.equivalent?(p,p,c)
    end
    assert_raises(ArgumentError){S.basis([[2]],[1])}
  end
end
