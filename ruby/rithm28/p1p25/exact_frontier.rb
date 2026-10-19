# frozen_string_literal: true
require_relative '../p1p23/three_agent'
require 'json'
# Exact half-lines in q for every one-deviation inequality. Uses Rational only.
module RithmExactFrontier
  module_function
  def intervals(k:Rational(3,4),p:Rational(1,2))
    plans=RithmThreeAgentInspection::PLANS
    out=[]
    plans.repeated_permutation(3) do |ps|
      v0=RithmThreeAgentInspection.expected(ps,k:k,q:0,p:p)[0]
      v1=RithmThreeAgentInspection.expected(ps,k:k,q:1,p:p)[0]
      low=Rational(0);high=nil;possible=true
      3.times do |i|
        plans.each do |alt|
          other=ps.dup;other[i]=alt
          n0=RithmThreeAgentInspection.expected(other,k:k,q:0,p:p)[0][i]-v0[i]
          n1=RithmThreeAgentInspection.expected(other,k:k,q:1,p:p)[0][i]-v1[i]
          slope=n1-n0
          if slope<0
            bound=-n0/slope
            high=high ? [high,bound].min : bound
          elsif slope>0
            low=[low,-n0/slope].max
          elsif n0<0
            possible=false
          end
        end
      end
      next unless possible && (high.nil? || (high>=0 && low<=high))
      out<<{'strategy_indices'=>ps.map{|x|plans.index(x)},'q_lower'=>low,
        'q_upper'=>high,'upper_unbounded'=>high.nil?}
    end
    out
  end
  # Exact symmetric mixed equilibrium ONLY in reduced two-active-player 2x2
  # subgame: each initially-A player chooses stay-A or inspect z then A/B;
  # initially-B player is FIXED. NOT equilibrium of original 3-agent game.
  def restricted_mixed(q:)
    raise ArgumentError unless q>=0 && q<=Rational(1,8)
    {'inspection_probability'=>Rational(1,8)-q,
      'other_agent_fixed'=>true,'full_game_mixed_nash_verified'=>false}
  end
end
if __FILE__==$PROGRAM_NAME
 puts JSON.pretty_generate(RithmExactFrontier.intervals.map{|r|r.transform_values{|x|x.is_a?(Rational) ? x.to_s : x}})
end
