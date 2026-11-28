require 'minitest/autorun'
require_relative 'r66_t38_empirical'
class TestR66T38Empirical < Minitest::Test
  E=RithmT38::Empirical
  def test_ratio_and_cluster_replay
    h={};%w[a b].each do |sid|
      %w[1 2 3].each{|t|h[[sid,t]]=sid=='a' ? [10,0,0,0,0,0] : [0,0,5,0,0,0]}
    end
    z=E.summarize(h,%w[a b],reps:100);assert_equal z,E.summarize(h,%w[a b],reps:100)
    assert_equal [30,0,15,0,0,0],z['all'][:counts]
    assert_in_delta 2.0/15,z['all'][:point][:p],1e-12
    assert_in_delta 1.0/30,z['all'][:point][:pair],1e-12
    assert_equal [0.0,1.0],z['all'][:cluster_percentile95][:no_departure]
    assert_equal 100,z['all'][:valid_bootstrap_draws]
    assert_raises(ArgumentError){E.stats([0]*6)}
  end
end
