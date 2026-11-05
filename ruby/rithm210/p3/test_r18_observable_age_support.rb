require 'minitest/autorun'
require_relative 'r18_observable_age_support'
class TestRithm210R18ObservableAgeSupport < Minitest::Test
  M=Rithm210R18ObservableAgeSupport
  def test_predefined_period_boundaries
    assert_equal :early,M.epoch(10)
    assert_equal :middle,M.epoch(11)
    assert_equal :middle,M.epoch(29)
    assert_equal :late,M.epoch(30)
  end
  def test_descriptive_support_not_an_effect
    values=[{epoch: :early,unchanged:false},{epoch: :early,unchanged:true},
      {epoch: :late,unchanged:false}]
    s=M.summarize(values)
    assert_equal 3,s[:all][:pairs]
    assert_equal 2,s[:all][:changed]
    assert_in_delta 2.0/3,s[:all][:distinct_fraction],1e-12
    assert_equal 1,s[:early][:unchanged]
    assert_equal 1,s[:late][:changed]
    refute s.key?(:middle)
  end
  def test_reject_nonoriginal_source
    require 'tempfile'
    Tempfile.create('source_integrity_fixture') do |tmp|
      tmp.write('not_original_csv');tmp.flush
      assert_raises(RuntimeError){M.rows(tmp.path)}
    end
  end
end
