require 'minitest/autorun'
require_relative 'r66_t33_history'
class TestR66T33History < Minitest::Test
  H=RithmT33::History
  def fixture(sid='1',paths=[[1,1,0,0,1,0],[1,0,1,0,1,0],[0,1,1,0,1,0],[0,1,1,1,1,0]])
    paths.each_with_index.flat_map{|a,t|a.each_with_index.map{|v,i|{'session'=>sid,'Group'=>'1','trt'=>'1','ID'=>i.to_s,'Period'=>(t+1).to_s,'RouteA'=>v.to_s}}}
  end
  def test_history_uses_past_actual_turnover_not_future
    a=fixture;b=a.map(&:dup);b.last['RouteA']='1'
    x=H.records(a,periods:4);y=H.records(b,periods:4)
    assert_equal x[0],y[0];assert_equal x[1][1],y[1][1];refute_equal x[1].last,y[1].last
    assert_equal 2,x[0][1][4].last;assert_equal 3,x[0][1][3].last
    assert_raises(RuntimeError){H.records(a.take(23),periods:4)}
  end
  def test_held_label_invariance
    r=H.records(fixture+fixture('2'),periods:4);k=r.first[1];a,h=H.fit(r);p=H.predict(k,a,h['1'])
    r[0]=[r[0][0],k,0];a,h=H.fit(r);assert_equal p,H.predict(k,a,h['1'])
    p.each{|q|assert_in_delta 1,q.sum,1e-12;assert q.all?(&:positive?)}
    assert_equal 4,H.evaluate(r)[:targets]
    assert_raises(RuntimeError){H.evaluate(r.take(2))}
  end
end
