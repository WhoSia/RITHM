require 'minitest/autorun'
require_relative 'group_residual_source_cv'
class TestRithm210GroupResidualSourceCV < Minitest::Test
  M = Rithm210GroupResidualSourceCV
  def test_synthetic_aggregate_and_cluster_bootstrap
    routes=[1,1,1,1,0,0]
    ys=[[0,0,0,0,0,0],[1,0,0,0,1,0]]
    rows=[1,2].flat_map do |s|
      [:baseline,:online_20,:online_80].map do |model|
        {session:s,model:model,epoch: :early,
         metrics:Rithm210GroupResidualWelfare.analyze(routes,ys[s-1],[0.2]*6)}
      end
    end
    a=M.bootstrap([1,2],rows,draws:100,seed:47)
    assert_equal 2,a[:selected_groups]
    assert_equal 100,a[:draws]
    point=a[:point]['baseline_early']
    pieces=[:linear_calibration,:diagonal_calibration,:same_route_pair,:opposite_route_pair].sum{|k|point[k]}
    assert_in_delta point[:welfare_error],pieces,1e-10
    assert_equal 2,point[:n]
  end
  def test_nonpositive_bootstrap_rejected
    assert_raises(ArgumentError){M.bootstrap([1],[],draws:0)}
  end
end
