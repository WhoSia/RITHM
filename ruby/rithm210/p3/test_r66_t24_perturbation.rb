require 'minitest/autorun'
require_relative 'r66_t24_perturbation'
class TestR66T24Perturbation < Minitest::Test
  P=RithmT24::Perturbation;W=RithmT24::Welfare
  def test_exact_grid_extrema
    # All 3-state distributions on denominator 6; extrema attainable on grid.
    rows=(0..6).flat_map{|a|(0..6-a).map{|b|[a,b,6-a-b].map{|x|Rational(x,6)}}}
    rows.each do |p|
      [0,Rational(1,6),Rational(1,2),1].each do |d|
        [-1,1].each do |s|
          [true,false].each do |support|
            v=[-2,3,1];x=P.extreme(p,v,d,s,support_only:support)
            candidates=rows.select{|r|r.zip(p).sum{|a,b|(a-b).abs}/2<=d && (!support || r.zip(p).all?{|a,b|b>0 || a==0})}
            best=candidates.map{|r|r.zip(v).sum{|a,b|a*b}}.sort
            assert_equal(s==1 ? best.last : best.first,x[:value]);assert_equal 1,x[:row].sum
            assert_operator x[:row].zip(p).sum{|a,b|(a-b).abs}/2,:<=,d
          end
        end
      end
    end
  end
  def test_policy_envelope_and_support_attack
    base=W.values(W.witness,40)[5];p=W.clock(W.witness,Rational(5,4));v=W.values(p,40)
    assert_equal [v,v],P.bounds(p,40,0)
    lo,hi=P.bounds(p,40,Rational(1,1000));assert_operator lo[5],:<,v[5];assert_operator hi[5],:>,base
    sl,sh=P.bounds(p,40,Rational(1,1000),support_only:true);assert_operator sl[5],:>=,lo[5];assert_operator sh[5],:<=,hi[5]
    assert_operator P.bounds(p,40,Rational(1,100000)).last[5],:<,base
    assert_equal [W::COST,W::COST],P.bounds(p,1,1)
  end
  def test_stationary_witness_near_certified_boundary
    base=W.values(W.witness,40)[5];p=W.clock(W.witness,Rational(5,4))
    assert_operator P.bounds(p,40,Rational(54,1_000_000)).last[5],:<,base
    delta=Rational(55,1_000_000);q=p.map(&:dup)
    (1..6).each{|i|q[i][i]-=delta;q[i][0]+=delta}
    W.matrix(q)
    q.zip(p).each{|a,b|assert_operator a.zip(b).sum{|x,y|(x-y).abs}/2,:<=,delta}
    assert_operator W.values(q,40)[5],:>,base
    assert_operator W.values(q,40)[5],:<=,P.bounds(p,40,delta).last[5]
  end

end
