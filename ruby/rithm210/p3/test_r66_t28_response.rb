require 'minitest/autorun'
require_relative 'r66_t28_response'
class TestR66T28Response < Minitest::Test
  R=RithmT28::Response;P=RithmT26::Policy
  def test_sharp_range_with_saturation
    rng=Random.new(2801)
    60.times do
      s=Rational(rng.rand(1..9),10);l=Rational(rng.rand((10*s).to_i..10),10);h=Rational(rng.rand((10*l).to_i..10),10)
      m=Rational(rng.rand(10..30),10);d=Rational(rng.rand(0..10),10)
      lo,hi=R.bounds(s,l,h,m,d)
      [lo,hi].each{|v,q,e|assert_equal v,R.switch(s,q,m,e);assert q.between?(l,h);assert e.between?(1-d,1+d)}
      (0..10).each do |i|
        q=l+(h-l)*Rational(i,10)
        [1-d,1,1+d].each do |e|
          x=R.switch(s,q,m,e);assert_operator x,:>=,lo.first;assert_operator x,:<=,hi.first
        end
      end
    end
  end
  def test_policy_robustness_brackets_and_boundary
    s=7r/200;h=53r/64
    assert_equal :improves,R.certify(s,s,h,5r/4,1718r/10000)[:status]
    x=R.certify(s,s,h,5r/4,11r/64);assert_equal :not_strict,x[:status];assert_equal x[:baseline],x[:cost]
    x=R.certify(s,s,h,5r/4,172r/1000);assert_operator x[:cost],:>,x[:baseline]
    assert_equal :improves,R.certify(s,s,h,3r/2,65r/1000)[:status]
    x=R.certify(s,s,h,3r/2,7r/100);assert_equal :not_strict,x[:status];assert_operator x[:cost],:>,x[:baseline]
    assert_raises(ArgumentError){R.bounds(s,s,h,0,0)}
    assert_raises(ArgumentError){R.certify(s,s,h,1,0,depth:-1)}
  end
end
