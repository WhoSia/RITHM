# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t17_loop'
class T17LoopTest < Minitest::Test
  O=RithmT17::Oracle; L=RithmT17::Loop; B=RithmT16::Belief
  def test_all_first_decisions_float_match_exact
    [Rational(1,5),Rational(1,2),Rational(4,5)].each do |rho|
      [:a,:b].each do |route|
        6.times do |k|
          [false,true].each do |seen|
            10.times do |i|
              y=Rational(13+2*i,2)-B.cost(k,route)
              p=seen ? (0..5).map { |j| j==k ? 1 : 0 } : B.posterior(B.binomial_base,route,y)
              e=B.expected_gain(B.predict(p,persistence:rho,base:B.binomial_base),route)
              q=L.update(L::BASE,route==:a,y.to_f,k,seen,rho.to_f)
              f=q.each_with_index.sum { |v,j| v*(3*j-11) }*(route==:a ? 1 : -1)
              assert_in_delta e.to_f,f,1e-12
              assert_equal e>0,f>1e-12
            end
          end
        end
      end
    end
  end
  def test_full_disclosure_inefficient_absorption
    [Rational(1,5),Rational(3,10),Rational(2,5),Rational(1,2)].each do |rho|
      L::CLOCKS.each do |clock|
        row=O.row(5,clock:clock,rho:rho,disclosure:1,response:1)
        assert_equal [0,0,0,0,0,1,0],row
      end
    end
  end
  def test_full_disclosure_exact_cost_reversal
    a=O.full_forecast(n:5,horizon:40,clock: :common,rho:Rational(4,5),response:1)
    b=O.full_forecast(n:5,horizon:40,clock: :common,rho:Rational(4,5),response:Rational(2,5))
    assert_operator a[:cost],:>,b[:cost]
    assert_equal 0,a[:final][4]
    assert_operator b[:final][4],:>,Rational(99,100)
  end
  def test_exact_first_step_sample
    L::CLOCKS.each do |clock|
      [0,0.5,1].each do |q|
        p=O.row(5,clock:clock,rho:Rational(4,5),disclosure:q,response:Rational(2,5))
        count=Array.new(7,0);reps=1500
        reps.times { |i| count[L.run(n:5,tape:L.tape(40000+i,2),clock:clock,rho:0.8,disclosure:q,response:0.4)[:final]]+=1 }
        p.each_with_index do |v,k|
          if v.zero?
            assert_equal 0,count[k]
          else
            m=v.to_f;assert_in_delta m,count[k].to_f/reps,5*Math.sqrt(m*(1-m)/reps)+0.002
          end
        end
      end
    end
  end
  def test_memory_control_and_no_future_leakage
    t=L.tape(42,5);p={n:5,clock: :fixed_three,rho:0.8,disclosure:1,response:0.4}
    assert_equal L.run(**p,tape:t,memory: :filter),L.run(**p,tape:t,memory: :reset)
    assert_equal L.run(**p,tape:t),L.run(**p,tape:t)
    assert_equal 3,L.run(**p,tape:[],memory: :filter)[:cost]
    assert_equal 0,L.run(**p.merge(response:0),tape:t)[:switches]
  end
  def test_zero_persistence_eliminates_history
    t=L.tape(4,10);p={n:5,clock: :independent,rho:0,disclosure:0,response:0.4,tape:t}
    assert_equal L.run(**p,memory: :filter),L.run(**p,memory: :reset)
  end
  def test_input_guards
    assert_raises(ArgumentError){O.row(7,clock: :common,rho:0.8,disclosure:0,response:1)}
    assert_raises(ArgumentError){L.run(n:5,tape:[],clock: :common,rho:1,disclosure:0,response:1)}
  end
end
