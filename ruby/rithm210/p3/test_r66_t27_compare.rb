require 'minitest/autorun'
require_relative 'r66_t27_compare'
class TestR66T27Compare < Minitest::Test
  C=RithmT27::Compare;F=RithmT27::Features
  def key(info)
    [[1,info,0],[1,info,0,3],[1,info,0,0],[1,info,0,3,0],[1,info,0,3,2],[1,info,0,3,1],[1,info,0,3,0],[1,info,0,3,0,2,1],[1,info,0,3,0,2,1,0]]
  end
  def test_held_label_invariance_and_no_redundant_update
    k=key(1);r=[['a',k,0],['b',k,1],['b',k,1]]
    a,h=C.fit(r);x=C.predict(k,a,h['a']);assert_equal x[1],x[6];assert_equal x[7],x[8]
    a,h=C.fit([['a',k,1],*r.drop(1)]);assert_equal x,C.predict(k,a,h['a'])
    assert_in_delta 0.75,x[0],1e-12
  end
  def test_baseline_reduces_to_t26
    k=key(0);r=[['a',k,0],['b',k,1],['b',k,0]]
    a,h=C.fit(r);b,j=RithmT26::Forecast.fit(r.map{|s,ks,y|[s,ks.take(4),y]})
    assert_equal RithmT26::Forecast.predict(k.take(4),b,j['a']),C.predict(k,a,h['a']).take(4)
    assert_equal 3,C.evaluate(r)[:records];assert_raises(RuntimeError){C.evaluate(r.take(1))}
  end
end
