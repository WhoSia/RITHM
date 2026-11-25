require 'minitest/autorun'
require_relative 'r66_t18_learning'
class TestR66T18 < Minitest::Test
  T=RithmT18
  def test_singleton_matches_t17_update
    [0.2,0.5,0.8].each do |rho|
      [:a,:b].each do |route|
        (0..5).each do |k|
          (0..9).each do |v|
            y=6.5+v-(route==:a ? k+1 : 2*(6-k))
            [nil,k].each do |seen|
              f=T::Filter.new([rho]); q=T::BASE.each_with_index.map { |p,j| (6..16).cover?(y+(route==:a ? j+1 : 2*(6-j))) && (seen.nil? || j==seen) ? p : 0.0 }
              z=q.sum; expected=q.each_with_index.map { |p,j| rho*p/z+(1-rho)*T::BASE[j] }
              f.observe(route,y,disclosed_k:seen)
              f.marginal.zip(expected).each { |a,b| assert_in_delta b,a,1e-12 }
            end
          end
        end
      end
    end
  end
  def test_exact_odds_and_escape
    f=T::Filter.new([0.2,0.8]); assert_in_delta 0,f.observe(:a,9,disclosed_k:4),1e-12
    1.upto(8) do |m|
      g=f.observe(:a,9,disclosed_k:4); o=T.repeated_odds(k:4,m:m).to_f
      assert_in_delta (0.2+0.8*o)/(1+o),f.mean_rho,1e-12
      assert_operator g,:>,0
    end
  end
  def test_full_forgetting_preserves_mass
    f=T::Filter.new([0.2,0.8]); 10.times do
      f.observe(:a,9,disclosed_k:4,forget:1)
      assert_in_delta 0.5,f.mean_rho,1e-12
      assert_in_delta 1,f.marginal.sum,1e-12
    end
  end
  def test_fixed_absorption_and_learning_escape
    tape=T.tape(201,40)
    T::CLOCKS.each do |clock|
      fixed=T.run(n:5,tape:tape,clock:clock,grid:[0.5],disclosure:1,response:1)
      learned=T.run(n:5,tape:tape,clock:clock,grid:[0.2,0.8],disclosure:1,response:1)
      assert_equal 120,fixed[:cost];assert_nil fixed[:first_exit];refute_nil learned[:first_exit]
    end
  end
  def test_private_update_and_guards
    f=T::Filter.new([0.2,0.8]); f.observe(:b,4)
    assert_in_delta 1,f.marginal.sum,1e-12
    assert_raises(ArgumentError){T::Filter.new([1])}
    assert_raises(ArgumentError){f.observe(:a,9,disclosed_k:6)}
    assert_raises(RuntimeError){f.observe(:a,99)}
  end
end
