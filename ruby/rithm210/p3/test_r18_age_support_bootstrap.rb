require 'minitest/autorun'
require_relative 'r18_age_support_bootstrap'
class TestRithm210R18AgeSupportBootstrap < Minitest::Test
  M=Rithm210R18AgeSupportBootstrap
  def example
    [1,2,3].flat_map{|s|[
      {session:s,epoch: :early,unchanged:s==1},
      {session:s,epoch: :late,unchanged:s==3}]}
  end
  def test_paired_session_resampling_and_seed
    a=M.summarize(example,draws:300,seed:7)
    b=M.summarize(example,draws:300,seed:7)
    assert_equal a,b
    assert_equal 3,a[:sessions]
    assert_in_delta 2.0/3,a[:early],1e-12
    assert_in_delta 2.0/3,a[:late],1e-12
    assert_in_delta 0,a[:difference],1e-12
  end
  def test_invalid_data
    assert_raises(ArgumentError){M.summarize(example,draws:0)}
    assert_raises(ArgumentError){M.summarize(example.first(2),draws:2)}
  end
end
