require 'minitest/autorun'
require_relative 'r23_group_memory_cv'
class TestR23GroupMemoryCV < Minitest::Test
  M=Rithm210R23GroupMemoryCV
  A=Rithm210R23ActorMemory
  def test_two_round_six_person_source_free_fixture
    groups={}
    (1..2).each do |period|
      groups[[9,1,period,1]]=(1..6).map do |id|
        choice=id<=3 ? 1 : 0
        {'ID'=>id.to_s,'RouteA'=>choice.to_s,'NumA'=>'3','trt'=>'3'}
      end
    end
    configs=[[1.0,5.0,0.0],[1.0,5.0,1.0]]
    rows=M.evaluate(groups,configs:configs)
    assert_equal 2,rows.size
    frequency=rows.find{|r|r[:model]==A.label(configs[0])}
    expected_first=Rithm210R20GroupBridge.score(Array.new(6,0.5),3)
    expected_second=Rithm210R20GroupBridge.score(
      Array.new(3,2.0/3)+Array.new(3,1.0/3),3)
    assert_in_delta (expected_first[:logloss]+expected_second[:logloss])/2,
      frequency[:logloss],1e-12
    assert_equal 2,frequency[:groups]
    groups[[9,1,2,1]][0]['NumA']='5'
    assert_raises(RuntimeError){M.evaluate(groups,configs:configs)}
  end
  def test_forecast_applied_before_current_group_update
    cfg=[1.0,5.0,0.0]
    groups={}
    groups[[9,1,1,1]]=(1..6).map do |id|
      {'ID'=>id.to_s,'RouteA'=>(id<=3 ? '1' : '0'),
       'NumA'=>'3','trt'=>'3'}
    end
    row=M.evaluate(groups,configs:[cfg]).first
    expected=Rithm210R20GroupBridge.score(Array.new(6,0.5),3)
    assert_in_delta expected[:logloss],row[:logloss],1e-12
  end
  def test_reject_empty_and_duplicate_config
    assert_raises(ArgumentError){M.evaluate({},configs:[])}
    assert_raises(ArgumentError){M.evaluate({},configs:[[1.0,5.0,0.0]]*2)}
  end
end
