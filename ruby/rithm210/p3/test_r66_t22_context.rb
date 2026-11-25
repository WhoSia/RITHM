require 'minitest/autorun'
require_relative 'r66_t22_context'
class TestR66T22Context < Minitest::Test
  C=RithmT22::Context
  def test_inactive_observations_not_used_in_active_row
    f=C::Rows.new(:conditional);p=C::Rows.new(:pooled)
    base=f.observe(5,false);p.observe(5,false)
    20.times { f.observe(5,false);p.observe(5,false) }
    assert_equal base,f.observe(5,true)
    assert_operator p.observe(5,true)[5],:>,base[5]
    assert_operator f.observe(3,true)[3],:>,0
    assert_operator f.observe(5,true)[3],:>,base[3]
  end
  def test_same_prior_and_future_noninterference
    C::MODES.each do |m|
      f=C::Rows.new(m);g=C::Rows.new(m)
      [true,false,true].zip([5,5,3]).each { |a,k| assert_equal f.observe(k,a),g.observe(k,a) }
      assert_in_delta 1,f.observe(4,true).sum,1e-12
    end
    assert_equal C::Rows.new(:pooled).observe(5,true),C::Rows.new(:conditional).observe(5,true)
  end
  def test_replay_uses_active_transitions_only
    path=[[[5]*6,[false]*6],[[5]*6,[true]*6],[[3]*6,[false]*6]]
    x=C.replay(path);assert x.values.all?{|_,cnt|cnt==6}
    assert_operator x[:conditional][0],:<,x[:pooled][0]
  end
  def test_no_opportunity_and_matched_tapes
    tape=Array.new(39){[[0.9]*6,[0.0]*6,0.9]}
    C::MODES.each do |m|
      r=C.run(tape:tape,clock: :common,response:1,mode:m);assert_equal 120,r[:cost];assert_equal 0,r[:switches]
      assert C.replay(r[:paths]).values.all?{|s,c|s==0 && c==0}
    end
    C::CLOCKS.product(C::MODES).each do |clock,mode|
      t=C.tape(123,40);a=C.run(tape:t,clock:clock,response:0.4,mode:mode);assert_equal a,C.run(tape:t,clock:clock,response:0.4,mode:mode)
    end
  end
end
