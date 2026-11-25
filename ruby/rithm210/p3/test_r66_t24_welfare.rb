require 'minitest/autorun'
require_relative 'r66_t24_welfare'
class TestR66T24Welfare < Minitest::Test
  W=RithmT24::Welfare
  def test_common_clock_exact_opposite_policy_welfare
    p=W.witness;base=W.values(p,40)[5]
    [Rational(4,5),Rational(1,2)].each do |q|
      a=W.clock(p,1/q);assert_equal p,W.clock(a,q)
      assert_operator W.values(a,2)[5],:<,W.values(p,2)[5]
    end
    assert_operator W.values(W.clock(p,Rational(5,4)),40)[5],:<,base
    assert_operator W.values(W.clock(p,2),40)[5],:>,base
  end
  def test_relative_policy_identified_without_saturation
    p=W.witness;m=Rational(5,4)
    [Rational(1,2),Rational(3,5),Rational(4,5)].each do |q|
      a=W.clock(p,1/q);assert_equal W.clock(p,m),W.clock(a,m*q)
    end
  end
  def test_cognitive_full_label_law_and_positive_private_gain
    s=Rational(7,200);base=W.values(W.cognitive(s),40)[5]
    [Rational(4,5),Rational(1,2)].each do |q|
      p=s/q;assert_operator W.active_gain(p)[0],:>,0;assert_operator W.active_gain(p)[1],:<,0
      # Integrate all latent eligibility masks for every labelled switch mask.
      32.times do |moves|
        m=5.times.count{|i|moves[i]==1};z=0
        32.times do |e|
          next unless (moves & ~e)==0
          n=5.times.count{|i|e[i]==1};z+=q**n*(1-q)**(5-n)*p**m*(1-p)**(n-m)
        end
        assert_equal s**m*(1-s)**(5-m),z
      end
    end
    assert_operator W.values(W.cognitive(s/Rational(4,5)),40)[5],:<,base
    assert_operator W.values(W.cognitive(s/Rational(1,2)),40)[5],:>,base
  end
  def test_bernstein_matches_direct_and_envelope_contains_grid
    p=W.witness;l=Rational(5,4);h=2
    [1,2,5,12,40].each do |n|
      c=W.bernstein(p,l,h,n,5);d=c.size-1
      assert_equal W.values(W.clock(p,l),n)[5],c.first
      assert_equal W.values(W.clock(p,h),n)[5],c.last
      e=W.envelope(c)
      21.times do |j|
        u=Rational(j,20);v=c.each_with_index.sum{|x,i|x*choose(d,i)*u**i*(1-u)**(d-i)}
        assert_equal W.values(W.clock(p,l+(h-l)*u),n)[5],v
        assert_operator v,:>=,e[:outer_low];assert_operator v,:<=,e[:outer_high]
      end
      assert_operator e[:attained_low]-e[:outer_low],:<=,Rational(1,100)
      assert_operator e[:outer_high]-e[:attained_high],:<=,Rational(1,100)
    end
  end
  def choose(n,k);(1..k).reduce(1){|v,i|v*(n-i+1)/i};end
  def test_guard
    assert_raises(ArgumentError){W.clock(W.witness,100)}
    assert_raises(ArgumentError){W.cognitive(-1)}
    assert_raises(ArgumentError){W.values(W.witness,0)}
  end
end
