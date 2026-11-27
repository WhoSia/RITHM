require 'minitest/autorun'
require_relative 'r66_t34_rollout'
class TestR66T34Rollout < Minitest::Test
  R=RithmT34::Rollout
  def test_forecast_against_explicit_paths
    c=R.fit([['a','1',[4,4,5,3,4,4,5,5,4]]]);p,v=R.forecast(c,4,'1',1,3,2)
    e=Array.new(7,0.0);cost=0.0
    (0..6).to_a.repeated_permutation(3) do |seq|
      w=1.0;n=4;seq.each_with_index{|j,i|w*=R.row(c,n,'1',1+i,2)[j];n=j}
      e[n]+=w;cost+=w*seq.sum{|j|R::COST[j]}
    end
    p.zip(e).each{|a,b|assert_in_delta a,b,1e-12};assert_in_delta v,cost,1e-12;assert_in_delta 1,p.sum,1e-12
  end
  def test_fit_excludes_first_target_and_held_session
    a=[['a','1',[0,4,5,3,4]],['b','1',[6,4,3,5,4]]];c=R.fit(a.take(1));assert_equal 0,c[0][[0]].sum;assert_equal 1,c[0][[4]][5];assert_equal 0,c[0][[4]][3]
    r=R.evaluate(a,horizons:[1,2]);assert_equal 6,r[:results][0][:models][0][:origins];assert_equal 4,r[:results][1][:models][0][:origins]
  end
  def test_recovery_counts
    a=R.recovery([['a','1',[4,5,4,5,3,4]]]);assert_equal [0,0,0,1,0,0,0],a[5][:counts].map.with_index{|v,i|i==3 ? v : 0};assert_equal 0.5,a[5][:return_to_four]
  end
end
