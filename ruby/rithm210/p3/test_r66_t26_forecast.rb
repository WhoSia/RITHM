require 'minitest/autorun'
require_relative 'r66_t26_forecast'
class TestR66T26Forecast < Minitest::Test
  F=RithmT26::Forecast
  def test_observation_contract
    r={'RouteA'=>'1','Informed'=>'0','trt'=>'1','profit'=>'9','NumA'=>'4','NumAnext'=>'2','switchWill'=>'1','Cost'=>'4'};prev={'RouteA'=>'0'}
    a=F.keys(r,prev);b=r.merge('NumA'=>'6','NumAnext'=>'6','switchWill'=>'0','Cost'=>'6')
    assert_equal a,F.keys(b,prev)
    assert_equal a[0],F.keys(r,{'RouteA'=>'1'})[0]
    refute_equal a[2],F.keys(r,{'RouteA'=>'1'})[2]
    refute_equal F.keys(r.merge('Informed'=>'1'),prev)[1],F.keys(b.merge('Informed'=>'1'),prev)[1]
  end
  def test_held_session_labels_do_not_affect_predictions
    k=[[1],[1,2],[1,0],[1,2,0]];a=[['a',k,0],['b',k,1],['b',k,1]]
    g,h=F.fit(a);p=F.predict(k,g,h['a']);g,h=F.fit([['a',k,1],*a.drop(1)])
    assert_equal p,F.predict(k,g,h['a']);assert_in_delta 0.75,p[0],1e-12
    assert_in_delta 11.0/14,p[1],1e-12;assert_in_delta p[1],p[2],1e-12
    assert_in_delta (2+12*(11.0/14))/14,p[3],1e-12
    assert_equal 3,F.evaluate(a)[:records]
    assert_raises(RuntimeError){F.evaluate(a.take(1))}
  end
  def test_chronological_record_target
    rows=[1,2,3].map{|t|{'session'=>'1','Group'=>'1','trt'=>'1','ID'=>'1','Period'=>t.to_s,'RouteA'=>(t==3 ? '0' : '1'),'Informed'=>'0','profit'=>'9','switchWill'=>'0'}}
    x=F.records(rows,periods:3);assert_equal 1,x.size;assert_equal 1,x[0][2];assert_equal 0,x[0][1][2].last
  end
end
