require 'minitest/autorun'
require_relative 'r66_t31_calibration'
class TestR66T31Calibration < Minitest::Test
  C=RithmT31::Calibration
  def test_residual_decomposition_and_bounds
    rng=Random.new(3102)
    100.times do
      ps=Array.new(6){0.01+0.98*rng.rand};a=Array.new(6){rng.rand(2)};r=C.metrics(ps,a)
      assert_operator r[:identity_error],:<,1e-12
      assert_operator r[:independent],:>=,r[:lower]-1e-12
      assert_operator r[:independent],:<=,r[:upper]+1e-12
      assert_in_delta C::G.metrics(ps,a)[:logloss],r[:losses][2],1e-12
      assert r[:losses].all?(&:finite?)
    end
  end
  def test_group_callback_preserves_original_scores
    p=C::G::P;m=p::M
    paths=3.times.flat_map do |sid|
      6.times.map do |i|
        route=Array.new(5){|t|(t+i+sid)%2};[sid,[1,0,route.first],m.events(route).map{|e|e+[0.0,false]},[sid,1,1]]
      end
    end
    expected=C::G.evaluate(paths,beta:0.15,iterations:2)
    got=C.evaluate(paths,iterations:2)
    assert_equal expected,got[:baseline]
    assert_in_delta expected[:session_mean][:logloss],got[:mixtures][2][:session_logloss],1e-12
  end
end
