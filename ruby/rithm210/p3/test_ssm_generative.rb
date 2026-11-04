require 'minitest/autorun'
require_relative 'ssm_generative'
class TestRithm210GenerativeSSM < Minitest::Test
  M=Rithm210GenerativeSSM
  def test_uniform_start_and_information_sets
    h={a:[],b:[],pair:[]}
    assert_includes [0,1],M.choose(h,informed:true,q:5,rng:Random.new(2))
    assert_includes [0,1],M.choose(h,informed:false,q:5,rng:Random.new(2))
    h={a:[-10.0],b:[],pair:[10.0]}
    assert_equal 1,M.choose(h,informed:true,q:5,rng:Random.new(2))
    assert_includes [0,1],M.choose(h,informed:false,q:5,rng:Random.new(2))
  end
  def test_simulation_determinism
    a=M.run(replicates:30,seed:20261104)
    assert_equal a,M.run(replicates:30,seed:20261104)
    assert_equal 6,a[:results].length
  end
end
