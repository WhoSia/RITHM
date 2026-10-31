require 'minitest/autorun'
class NumericAverageTest < Minitest::Test
  def mean(values)
    raise ArgumentError if values.empty?
    values.sum.to_f / values.size
  end
  def test_fractional_mean_not_truncated
    observed=[1,2,2,1,2,1]
    assert_in_delta 1.5,mean(observed),1e-12
  end
  def test_sample_5616_fractional_mean
    assert_in_delta 1.586360398860399,8909.to_f/5616,1e-12
  end
end
