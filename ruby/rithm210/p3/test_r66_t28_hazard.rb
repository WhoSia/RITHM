require 'minitest/autorun'
require_relative 'r66_t28_hazard'
class TestR66T28Hazard < Minitest::Test
  H=RithmT28::Hazard
  def rows(routes=[1,1,0,0,1,1],sid:'1')
    routes.each_with_index.map{|a,i|{'session'=>sid,'Group'=>'1','trt'=>'1','ID'=>'1','Period'=>(i+1).to_s,'RouteA'=>a.to_s,'Informed'=>'0','profit'=>'9','NumA'=>(a+3).to_s}}
  end
  def test_chronological_directional_exposure_and_duration
    r=H.records(rows,periods:6)
    assert_equal [1,0,1,0],r.map(&:last)
    assert_equal [[1,1],[2,0],[1,1],[2,1]],r.map{|x|x[2][3].last(2)}
    assert_equal [1,0,1,0],r.map{|x|x[2][5].last}
    assert_equal [0,1,1,1],r.map{|x|x[2][6].last}
  end
  def test_no_hidden_future_or_lead_features
    a=rows;b=a.map(&:dup);b[3]['RouteA']='1';b[2]['NumA']='6';b[2]['switchWill']='0'
    x=H.records(a,periods:6);y=H.records(b,periods:6)
    assert_equal x[0],y[0];assert_equal x[1][2],y[1][2];refute_equal x[1].last,y[1].last
    assert_raises(RuntimeError){H.records(a.take(4),periods:6)}
  end
  def test_held_label_invariance_and_baseline
    r=H.records(rows+rows(sid:'2'),periods:6);all,held=H.fit(r);k=r.first[2]
    p=H.predict(k,all,held['1']);r[0]=r[0].take(3)+[1-r[0].last]
    all,held=H.fit(r);assert_equal p,H.predict(k,all,held['1'])
    old=r.map{|sid,_,ks,y|[sid,[ks[0],ks[1],ks[0]+[0],ks[1]+[0]],y]}
    a,b=RithmT26::Forecast.fit(old);assert_equal RithmT26::Forecast.predict(old.first[1],a,b['1']).take(2),p.take(2)
    assert_equal 8,H.evaluate(r)[:records]
    assert_raises(RuntimeError){H.evaluate(r.take(4))}
  end
end
