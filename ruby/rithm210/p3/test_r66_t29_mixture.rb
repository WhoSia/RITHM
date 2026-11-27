require 'minitest/autorun'
require_relative 'r66_t29_mixture'
class TestR66T29Mixture < Minitest::Test
  M=RithmT29::Mixture
  def test_predict_matches_prefix_likelihood
    types=[[0.2,0.7],[0.8,0.3]];w=[0.3,0.7];ev=M.events([0,0,0,1,0,1,1,1,0]);m=0.5
    M.predict(ev,w,m,types).each_with_index do |p,i|
      ls=M.likelihood(ev.take(i),m,types);a,d,_=ev[i];mass=w.zip(ls).map{|x,y|x*y}
      expected=mass.each_with_index.sum{|x,j|x*M.probability(types[j][a],d,m)}/mass.sum
      assert_in_delta expected,p,1e-14
    end
  end
  def test_fit_and_guards
    w=M.fit([[0.9,0.1],[0.8,0.2]],iterations:100)
    assert_in_delta 1,w.sum,1e-14;assert_operator w.first,:>,0.9
    assert_raises(ArgumentError){M.fit([[0,0]])}
    assert_raises(ArgumentError){M.fit([])}
    assert_raises(RuntimeError){M.evaluate([[1,[1,0],[0,1,0]]])}
  end
  def test_online_prediction_prefix_invariance
    a=M.events([0,0,1,0,1]);b=M.events([0,0,1,1,1]);w=Array.new(M::TYPES.size,1.0/M::TYPES.size)
    assert_equal M.predict(a,w,1).take(3),M.predict(b,w,1).take(3)
  end
end
