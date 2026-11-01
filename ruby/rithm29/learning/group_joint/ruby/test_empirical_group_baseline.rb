require 'minitest/autorun'
require_relative 'empirical_group_baseline'
class BaselineTest < Minitest::Test
 def test_probabilities
  fit=RithmEmpiricalBaseline.fitted([{trt:1,prev:3,up:1,down:0},{trt:2,prev:5,up:0,down:1}])
  [0,3,6].each do |prev|
   [true,false].each do |conditional|
    p=RithmEmpiricalBaseline.probabilities(fit,1,prev,conditional:conditional)
    assert_in_delta 1.0,p.values.sum,1e-12
    assert p.values.all?{|v|v>0}
   end
  end
 end
 def test_feasibility
  fit=RithmEmpiricalBaseline.fitted([{trt:1,prev:0,up:1,down:0}])
  p=RithmEmpiricalBaseline.probabilities(fit,1,0,conditional:true)
  assert_equal (0..6).map{|u|[u,0]},p.keys
 end
end
