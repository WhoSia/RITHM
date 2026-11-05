require 'minitest/autorun'
require_relative 'r18_design_feasibility'
class TestRithm210R18DesignFeasibility < Minitest::Test
  M=Rithm210R18DesignFeasibility
  def test_historical_proxy
    x=M.compare
    assert_equal 35,x[:feedback][:per_condition]
    assert_equal 70,x[:feedback][:total]
    assert_equal 69,x[:interaction][:per_condition]
    assert_equal 276,x[:interaction][:total]
  end
  def test_effect_sensitivity
    assert_equal 138,M.clusters_each(sd:M::HISTORICAL_SD,effect:10,contrast: :feedback)
    assert_equal 275,M.clusters_each(sd:M::HISTORICAL_SD,effect:10,contrast: :interaction)
    assert_equal 16,M.clusters_each(sd:M::HISTORICAL_SD,effect:30,contrast: :feedback)
    assert_equal 31,M.clusters_each(sd:M::HISTORICAL_SD,effect:30,contrast: :interaction)
  end
  def test_rejections
    assert_raises(ArgumentError){M.clusters_each(sd:0,effect:10)}
    assert_raises(ArgumentError){M.clusters_each(sd:30,effect:0)}
    assert_raises(ArgumentError){M.clusters_each(sd:30,effect:10,contrast: :unknown)}
  end
end
