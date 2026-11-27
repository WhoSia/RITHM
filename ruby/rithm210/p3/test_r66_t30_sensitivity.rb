require 'minitest/autorun'
require_relative 'r66_t30_sensitivity'
class TestR66T30Sensitivity < Minitest::Test
  S=RithmT30::Sensitivity
  def test_paired_estimand_and_missing_strata
    a={1=>[2,0.5,0,{0=>[2,1.0,0],1=>[0,0,0]}],2=>[4,0.5,0,{0=>[1,0.5,0],1=>[3,1.5,0]}]}
    b={1=>[2,0.4,0,{0=>[2,0.8,0],1=>[0,0,0]}],2=>[4,0.55,0,{0=>[1,0.4,0],1=>[3,1.8,0]}]}
    r=S.contrast(a,b);assert_in_delta(-0.025,r[:mean],1e-12);assert_equal 1,r[:better]
    assert_in_delta(-0.1,r[:by_information][0][:mean],1e-12);assert_equal 2,r[:by_information][0][:better]
    assert_in_delta(0.1,r[:by_information][1][:mean],1e-12);assert_equal 1,r[:by_information][1][:sessions]
    assert_raises(ArgumentError){S.contrast(a,b.take(1).to_h)}
  end
end
