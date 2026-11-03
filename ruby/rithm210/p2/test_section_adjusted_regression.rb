require 'minitest/autorun'
require_relative 'section_adjusted_regression'
class TestRithm210SectionAdjustedRegression < Minitest::Test
  M=Rithm210SectionAdjustedRegression
  def panels
    perms=[1,2,3].permutation.to_a
    (0...24).map do |s|
      p=perms[s%6]
      (2..4).map do |section|
        t=p[section-2]
        {session:s,section:section,treatment:t,
          y:s*0.01+(t==2 ? -0.005 : 0)+(t==3 ? -0.007 : 0)+
            (section==3 ? 0.003 : 0)+(section==4 ? 0.004 : 0)}
      end
    end
  end
  def test_recovers_coefficients_with_arbitrary_session_intercepts
    b=M.coefficients(panels)
    [-0.005,-0.007,0.003,0.004].each_with_index{|v,i|assert_in_delta v,b[i],1e-10}
  end
  def test_reject_singular_design
    assert_raises(RuntimeError){M.solve([[0.0,0.0],[0.0,0.0]],[0.0,0.0])}
  end
  def test_session_resampling_reproducible
    a=M.interval(panels,draws:100)
    assert_equal a,M.interval(panels,draws:100)
  end
end
