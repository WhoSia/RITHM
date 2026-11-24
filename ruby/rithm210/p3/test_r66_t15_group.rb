# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t15_group'
class T15GroupTest < Minitest::Test
  G=RithmT15::Group; S=RithmT12::Schedules
  def test_initial_law
    (0..6).each { |n| assert_equal 1,G.initial(n).values.sum; assert_equal 1,G.occupancy(G.initial(n))[n] }
  end
  def test_first_transition_equivalence
    G::CLOCKS.each do |clock|
      (0..6).each do |n|
        assert_equal G.forecast(n:n,horizon:2,clock:clock,mechanism: :fixed),G.forecast(n:n,horizon:2,clock:clock,mechanism: :reset)
      end
    end
  end
  def test_activation_matches_labelled_oracle
    [[:common,S.common],[:independent,S.independent],[:fixed_three,S.fixed_count(3)]].each do |clock,w|
      (0..6).each do |l|
        (0..6-l).each do |h|
          counts=Hash.new(0)
          w.each_with_index do |p,mask|
            next if p.zero?
            i=(0...l).count { |j| (mask & (1<<j))!=0 }
            j=(l...l+h).count { |k| (mask & (1<<k))!=0 }
            counts[[i,j]]+=p
          end
          assert_equal counts,G.activation(l,h,clock)
        end
      end
    end
  end
  def test_all_states_normalized
    (0..6).each do |n|
      G.initial(n).keys.each do |s|
        G::CLOCKS.each do |clock|
          [:fixed,:reset,:partial].each do |m|
            row=G.row(s,clock,m,reset_probability: m==:partial ? Rational(1,2) : nil)
            assert_equal 1,row.values.sum
            assert row.keys.all? { |x| x.sum==6 && x.min>=0 }
          end
        end
      end
    end
  end
  def test_optimum_absorbing
    G::CLOCKS.each { |c| assert_equal 0,G.forecast(n:4,horizon:40,clock:c,mechanism: :reset)[:congestion] }
  end
  def test_direction_reversal_across_clocks
    G::CLOCKS.each do |c|
      a=G.forecast(n:5,horizon:40,clock:c,mechanism: :fixed)[:congestion]
      b=G.forecast(n:5,horizon:40,clock:c,mechanism: :reset)[:congestion]
      assert_operator a,c==:common ? :> : :<,b
    end
  end
  def test_partial_reset_endpoints
    G::CLOCKS.each do |c|
      [0,1].each do |r|
        a=G.forecast(n:5,horizon:8,clock:c,mechanism: :partial,reset_probability:r)
        b=G.forecast(n:5,horizon:8,clock:c,mechanism:r==0 ? :fixed : :reset)
        assert_equal b,a
      end
    end
  end
  def test_invalid_inputs
    assert_raises(ArgumentError){G.row([1,2,3,0],:common,:partial,reset_probability:2)}
    assert_raises(ArgumentError){G.row([1,2,3,0],:other,:fixed)}
    assert_raises(ArgumentError){G.row([1,2,3,1],:common,:fixed)}
  end
end
