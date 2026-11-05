require 'minitest/autorun'
require_relative 'qi_abc_session_contrast'
class TestRithm210QiABCSessionContrast < Minitest::Test
  M=Rithm210QiABCSessionContrast
  def sample(epoch,a,b,c)
    {epoch:epoch,a:a,b:b,c:c}
  end
  def test_paired_deltas_and_no_cross_session_leakage
    by={1=>[sample(:early,0.1,0.3,0.2),sample(:late,0.5,0.9,0.4)],
        2=>[sample(:early,0.6,0.8,0.6),sample(:late,0.1,0.4,0.2)]}
    x=M.bootstrap([1,2],by,draws:100,seed:8)
    assert_equal 4,x[:all][:n]
    assert_in_delta(-0.025,x[:all][:contrasts][:a_minus_c][:delta],1e-12)
    assert_in_delta(0.25,x[:all][:contrasts][:b_minus_c][:delta],1e-12)
    assert_in_delta(0.275,x[:all][:contrasts][:b_minus_a][:delta],1e-12)
    assert_equal 2,x[:early][:n]
    assert_equal 2,x[:late][:n]
  end
  def test_same_seed_same_result_and_empty_resamples
    by={1=>[sample(:early,0.2,0.4,0.1)],
        2=>[sample(:late,0.3,0.7,0.4)]}
    assert_equal M.bootstrap([1,2],by,draws:30,seed:12),
                 M.bootstrap([1,2],by,draws:30,seed:12)
    assert_raises(ArgumentError){M.bootstrap([],{},draws:2)}
    assert_raises(ArgumentError){M.bootstrap([1],{},draws:0)}
    assert_raises(RuntimeError){M.bootstrap([1],{},draws:10)}
  end
end
