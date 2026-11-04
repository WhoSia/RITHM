require 'minitest/autorun'
require_relative 'welfare_variance_bootstrap'
class TestRithm210WelfareDecomposition < Minitest::Test
  M=Rithm210WelfareDecomposition
  def synthetic
    (1..24).flat_map do |s|
      [1,3].flat_map do |trt|
        %w[early late].map do |ep|
          {session:s,treatment:trt,epoch:ep,
            n:(trt==3 && ep=='early' ? 3 : 4)}
        end
      end
    end
  end
  def test_exact_mean_variance_decomposition
    stats=M.sufficient_statistics(synthetic)
    sessions=(1..24).to_a
    result=M.differences(stats,sessions)
    assert_equal 3,result[:full_bias_decline]
    assert_equal 0,result[:full_dispersion_decline]
    assert_equal 3,result[:full_total_decline]
    assert_equal 3,result[:full_vs_no_total_decline]
  end
  def test_perfectly_bimodal_around_optimum_is_dispersion_not_mean_bias
    rows=(1..24).flat_map do |s|
      [{session:s,treatment:3,epoch:'early',n:3},
       {session:s,treatment:3,epoch:'early',n:5}]
    end
    stats=M.sufficient_statistics(rows)
    a=M.components(stats,(1..24).to_a,3,'early')
    assert_in_delta 0,a[:bias],1e-12
    assert_in_delta 3,a[:dispersion],1e-12
    assert_in_delta 3,a[:total],1e-12
  end
end
