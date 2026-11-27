require 'minitest/autorun'
require_relative 'r66_t30_payoff'
class TestR66T30Payoff < Minitest::Test
  P=RithmT30::Payoff;M=RithmT29::Mixture
  def test_legal_information
    r={'RouteA'=>'1','Informed'=>'0','trt'=>'1','profit'=>'9','NumA'=>'4'}
    assert_equal P.gain(r),P.gain(r.merge('NumA'=>'6','NumAnext'=>'0','switchWill'=>'1'))
    assert_equal(-2.0,P.gain(r.merge('Informed'=>'1')))
    assert_equal 2.0,P.gain(r.merge('RouteA'=>'0','Informed'=>'1','NumA'=>'3'))
  end
  def test_zero_beta_equivalence_and_sequential_prefix
    ev=M.events([0,0,0,1,0,0,0,1]).map{|a,d,y|[a,d,y,3.0,false]};types=[[0.2,0.7],[0.8,0.3]];w=[0.3,0.7]
    ps,l=P.prepare(ev,0.0,1.0,types)
    M.likelihood(ev,1.0,types).zip(l).each{|a,b|assert_in_delta a,b,1e-15}
    M.predict(ev,w,1.0,types).zip(P.predict(ev,ps,w)).each{|a,b|assert_in_delta a,b,1e-15}
    changed=ev.map(&:dup);changed[-1][2]=1-ev[-1][2];ps2,_=P.prepare(changed,0.15,1.0,types);ps1,_=P.prepare(ev,0.15,1.0,types)
    assert_equal P.predict(ev,ps1,w),P.predict(changed,ps2,w)
  end
  def test_direction_and_initial_spell
    type=[[0.2,0.7]];e=[0,3,0,2.0,true]
    assert_equal P.probabilities(e,0.15,0.5,type),P.probabilities(e,0.15,1.0,type)
    assert_operator P.probabilities(e,0.15,1.0,type).first,:>,P.probabilities(e,0,1.0,type).first
    e[-1]=false;assert_operator P.probabilities(e,0.15,0.5,type).first,:<,P.probabilities(e,0.15,1.0,type).first
  end
  def test_held_session_and_matched_targets
    routes=[[0,0,1,0,1],[1,1,0,1,1],[0,1,1,0,0]]
    a=routes.each_with_index.map{|r,i|[i,[1,0],r]}
    b=a.map{|sid,key,r|[sid,key+[r.first],M.events(r).map{|x|x+[0.0,false]}]}
    expected=M.evaluate(a,iterations:12);got=P.evaluate(b,iterations:12)
    assert_equal expected[:records],got[:records]
    assert_in_delta expected[:session_logloss],got[:session_logloss],1e-14
    assert_raises(ArgumentError){P.evaluate(b,beta:Float::NAN)}
  end
end
