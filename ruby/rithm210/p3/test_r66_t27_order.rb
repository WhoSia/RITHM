require 'minitest/autorun'
require_relative 'r66_t27_order'
class TestR66T27Order < Minitest::Test
  O=RithmT27::Order
  def test_exact_exchangeable_expectation
    (2..9).each do |n|
      (0..n).each do |m|
        a=(0...n).to_a.combination(m).map{|ids|O.adjacency(Array.new(n){|i|ids.include?(i) ? 1 : 0})}
        assert_equal Rational(a.sum(&:first),a.size),a.first.last
      end
    end
  end
  def test_markov_expectation_against_uniform_transition_count_classes
    (3..9).each do |n|
      classes=(0...2**n).map{|m|Array.new(n){|i|m[i]}}.group_by{|r|[r.first,r.each_cons(2).tally]}
      classes.each_value do |paths|
        expected=Rational(paths.sum{|r|r.each_cons(3).count{|a,b,c|a!=b && b!=c}},paths.size)
        paths.each{|r|assert_equal expected,O.markov_expected(r)}
      end
    end
  end
  def test_trajectory_and_guards
    rows=[0,1,0,0,0].each_with_index.map{|a,i|{'session'=>'1','Group'=>'1','trt'=>'1','ID'=>'1','Period'=>(i+1).to_s,'RouteA'=>a.to_s}}
    r=O.summarize(rows,periods:5);assert_equal 1,r[:whole][:adjacent_switches];assert_equal 0.5,r[:whole][:exchangeable_expected]
    assert_equal 1,r[:early][:adjacent_switches];assert_equal 0,r[:late][:adjacent_switches]
    assert_raises(ArgumentError){O.adjacency([2,1])};assert_raises(RuntimeError){O.summarize(rows.take(4),periods:5)}
  end
end
