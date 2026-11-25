require 'minitest/autorun'
require_relative 'r66_t27_features'
class TestR66T27Features < Minitest::Test
  F=RithmT27::Features
  def rows(routes=[1,1,0,0,1,1],info:0)
    routes.each_with_index.map{|a,i|{'session'=>'1','Group'=>'1','trt'=>'1','ID'=>'1','Period'=>(i+1).to_s,'RouteA'=>a.to_s,'Informed'=>info.to_s,'profit'=>'9','NumA'=>(a+3).to_s}}
  end
  def test_duration_and_propensity
    x=F.records(rows,periods:6)
    assert_equal 4,x.size
    assert_equal [1,0,1,0],x.map{|r|r[2]}
    assert_equal [1,0,1,0],x.map{|r|r[1][4].last}
    assert_equal [2,1,2,1],x.map{|r|r[1][5].last}
  end
  def test_no_future_or_hidden_features
    a=rows;b=a.map(&:dup);b[3]['RouteA']='1';b[0]['NumA']='6';b[2]['switchWill']='999'
    x=F.records(a,periods:6);y=F.records(b,periods:6)
    assert_equal x[0],y[0];assert_equal x[1][1],y[1][1];refute_equal x[1][2],y[1][2]
  end
  def test_filter_reset_and_full_disclosure
    a=F.posterior(F::BASE,1<<3,0.5);b=F.posterior(F::BASE,1<<0,0.5)
    assert_equal F.posterior(a,1<<4,0.5),F.posterior(b,1<<4,0.5)
    assert_equal F::BASE,F.posterior(a,1<<4,0)
    assert_raises(RuntimeError){F.posterior(a,0,0.5)}
    assert_raises(RuntimeError){F.records(rows.take(3),periods:6)}
  end
end
