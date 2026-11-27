require 'minitest/autorun'
require_relative 'r66_t36_measurement'
class TestR66T36Measurement < Minitest::Test
  M=RithmT36::Measurement; S=M::S
  def test_exact_simplex_and_moment_fiber
    a=[[1,1,1],[0,1,2]];b=[1,1];v=M.vertices(a,b)
    assert_equal [[0,1,0],[1r/2,0,1r/2]].sort,v.sort
    assert_equal 1,M.width(v,[0,1,4]);assert_equal 0,M.width(v,[0,1,2])
    assert_equal 0,M.width(M.vertices(a+[[0,1,4]],b+[2]),[0,1,4])
  end
  def test_random_fibers_contain_reference
    rng=Random.new(3602)
    50.times do
      w=Array.new(7){rng.rand(1..9)};q=w.map{|x|Rational(x,w.sum)};a=[Array.new(7,1),(0..6).to_a,(0..6).map{|n|n*n}];v=Array.new(7){rng.rand(20)}
      vs=M.vertices(a,S.apply(a,q));vals=vs.map{|p|S.dot(p,v)};assert S.dot(q,v).between?(*vals.minmax)
      assert_equal 0,M.width(M.vertices(a+[v],S.apply(a+[v],q)),v)
    end
  end
end
