require 'minitest/autorun'
require_relative 'r18_cluster_power_gate'
class TestRithm210R18ClusterPowerGate < Minitest::Test
  M=Rithm210R18ClusterPowerGate
  def test_four_arm_gaussian_normal_approximation
    assert_equal 69,M.clusters_per_arm(sd:29.58918598975362,target:20)
    assert_equal 275,M.clusters_per_arm(sd:29.58918598975362,target:10)
    assert_in_delta 67.6848117688,M.minimum_detectable(sd:29.58918598975362,clusters_per_arm:6),1e-8
  end
  def test_sessions_versus_group_paths
    paths=(1..24).flat_map{|s|[0,1].map{|j|{session:s,total:1000+s+j}}}
    a=M.summarize(paths)
    assert_equal 24,a[:sessions]
    assert_equal 48,a[:group_paths]
    assert_equal({2=>24},a[:group_paths_per_session])
    assert_in_delta 1013.0,a[:mean_group_total],1e-12
  end
  def test_irregular_group_paths_per_session_valid
    paths=[]
    (1..24).each do |s|
      count=s<=4 ? 1 : s<=8 ? 3 : 2
      count.times{|i|paths<<{session:s,total:1000+s+i}}
    end
    x=M.summarize(paths)
    assert_equal 48,x[:group_paths]
    assert_equal({1=>4,3=>4,2=>16},x[:group_paths_per_session])
  end
  def test_bad_planning_values_rejected
    assert_raises(ArgumentError){M.sample_sd([1])}
    assert_raises(ArgumentError){M.clusters_per_arm(sd:0,target:10)}
    assert_raises(ArgumentError){M.clusters_per_arm(sd:10,target:0)}
    assert_raises(ArgumentError){M.minimum_detectable(sd:10,clusters_per_arm:1)}
  end
end
