require 'minitest/autorun'
require_relative 'r66_t37_sensor_cost'
class TestR66T37SensorCost < Minitest::Test
  S=RithmT37::SensorCost
  def test_noise_and_cost
    assert_equal 1r/2,S.noisy(1r/10,1r/2)
    assert_equal 1r/10,S.noisy(1r/10,0)
    assert_raises(ArgumentError){S.noisy(1r/10,3r/4)}
    z=S.audit;n=z[:sample_sizes]
    original=S::R.audit;z[:results][0][:risks].each{|k,v|assert_equal [original[:no_data],*original[:events][k][:risks].values],v}
    z[:results].each_cons(2){|a,b|a[:risks].each_key{|k|a[:risks][k].zip(b[:risks][k]).each{|x,y|assert_operator x,:<=,y+1e-12}}}
    z[:results].each do |r|
      r[:grid_optima].each do |o|
        oracle=r[:risks].values.flat_map{|v|v.zip(n).map{|x,j|x+j*o[:cost_per_sample]}}.min
        assert_in_delta oracle,o[:total],1e-12
      end
    end
  end
end
