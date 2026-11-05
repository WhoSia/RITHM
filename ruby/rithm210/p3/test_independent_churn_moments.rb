require 'minitest/autorun'
require_relative 'independent_churn_moments'
class TestRithm210IndependentChurnMoment < Minitest::Test
 M=Rithm210IndependentChurnMoment
 def test_endpoints_and_full_distribution
  [0.0,0.12,0.5,1.0].each do |e|
    law=M.exact_distribution(e)
    assert_in_delta 1.0,law.values.sum,1e-12
    p=M.from_gross(6*e)
    assert_in_delta p[:no_switch],law[[0,0]],1e-12
    cancel=law.sum{|(u,d),mass|u==d && u>0 ? mass : 0}
    assert_in_delta p[:cancellation],cancel,1e-12
    loss=law.sum{|(u,d),mass|3*(u-d)**2*mass}
    assert_in_delta p[:next_excess],loss,1e-12
  end
 end
 def test_source_epoch_moments_without_fit_to_welfare
  a=M.from_gross(1.3571428571428572)
  b=M.from_gross(0.5836575875486381)
  assert_in_delta 0.21468634,a[:no_switch],1e-6
  assert_in_delta 0.15615300,a[:cancellation],1e-6
  assert_in_delta 3.76445578,a[:next_excess],1e-6
  assert_in_delta 0.54116434,b[:no_switch],1e-6
  assert_in_delta 0.05070947,b[:cancellation],1e-6
  assert_in_delta 1.69419673,b[:next_excess],1e-6
 end
 def test_bad_probability
  assert_raises(ArgumentError){M.from_gross(-1)}
  assert_raises(ArgumentError){M.exact_distribution(1.2)}
 end
end
