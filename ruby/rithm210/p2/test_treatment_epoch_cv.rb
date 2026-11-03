require 'minitest/autorun'
require_relative 'treatment_epoch_cv'
class TestRithm210TreatmentEpochCV < Minitest::Test
  M=Rithm210TreatmentEpochCV
  def test_epoch_partition
    assert_equal 'early',M.epoch(1)
    assert_equal 'early',M.epoch(10)
    assert_equal 'middle',M.epoch(11)
    assert_equal 'middle',M.epoch(29)
    assert_equal 'late',M.epoch(30)
    assert_equal 'late',M.epoch(39)
  end
  def test_whole_session_weighted_bootstrap
    rows=[{session:3,delta:-1.0},{session:4,delta:1.0},{session:4,delta:1.0},{session:4,delta:1.0}]
    r=M.bootstrap(rows,key: :delta,draws:200)
    assert_in_delta 0.5,r[:mean],1e-12
    assert_equal 2,r[:clusters]
  end
  def test_bootstrap_repeatability
    rows=[{session:3,delta:-1.0},{session:4,delta:1.0}]
    assert_equal M.bootstrap(rows,key: :delta,draws:100),M.bootstrap(rows,key: :delta,draws:100)
  end
end
