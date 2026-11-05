# frozen_string_literal: true
# R17E: latent binary group shock creates residual pair dependence even when
# the six individual choices are independent CONDITIONAL on that shock.
require_relative 'smooth_signal_clock'
module Rithm210LatentShockResidualCounterexample
  module_function
  M=Rithm210SmoothSignalClock
  B=Rithm210UpdateClockSignalFactorial
  def actor_scenarios(mask:,strength:,tremble:,shock_amplitude:,biases:Array.new(6,0.0))
    n=B.occupancy(mask)
    raise ArgumentError,'positive shock amplitude' unless shock_amplitude.positive?
    (0..5).map do |i|
      route_a=(mask & (1<<i))!=0
      plus=M.probability(route_a,n,actor:i,strength:strength,tremble:tremble,biases:biases,shock:shock_amplitude)
      minus=M.probability(route_a,n,actor:i,strength:strength,tremble:tremble,biases:biases,shock:-shock_amplitude)
      {route_a:route_a,p_plus:plus,p_minus:minus,marginal:(plus+minus)/2.0,delta:plus-minus}
    end
  end
  def covariance(a,b)
    0.25*a.fetch(:delta)*b.fetch(:delta)
  end
  def summary(mask:15,strength:0.7,tremble:0.05,shock_amplitude:2.0,biases:Array.new(6,0.0))
    actors=actor_scenarios(mask:mask,strength:strength,tremble:tremble,shock_amplitude:shock_amplitude,biases:biases)
    same=[];opposite=[]
    actors.each_with_index do |a,i|
      (i+1...6).each do |j|
        b=actors[j]
        (a[:route_a]==b[:route_a] ? same : opposite)<<covariance(a,b)
      end
    end
    mixture=M.expected_excess(M.occupancy_distribution(mask,clock: :simultaneous,
      signal: :frozen,strength:strength,tremble:tremble,biases:biases,shock_amplitude:shock_amplitude))
    # Independent fitted marginals: same actor probabilities but no group shock.
    independent=actors.each_with_index.reduce({mask=>1.0}) do |dist,(actor,i)|
      nxt=Hash.new(0.0)
      dist.each do |state,mass|
        nxt[state]+=mass*(1-actor[:marginal])
        nxt[state^(1<<i)]+=mass*actor[:marginal]
      end
      nxt
    end
    hist=Array.new(7,0.0)
    independent.each{|state,p|hist[B.occupancy(state)]+=p}
    baseline=M.expected_excess(hist)
    signed=6.0*(same.sum-opposite.sum)
    raise 'welfare identity failed' unless (mixture-baseline-signed).abs<1e-8
    {mean_same_route_cov:same.sum/same.size,mean_opposing_route_cov:opposite.sum/opposite.size,
     signed_pair_excess_welfare:signed,shock_mixture_excess:mixture,
     independent_marginal_excess:baseline,
     interpretation:'Conditional actor independence and unobserved common shock; NO direct peer influence.'}
  end
end
