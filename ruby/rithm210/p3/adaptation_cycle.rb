# frozen_string_literal: true
# RITHM-2.10 P3-R1: exact two-cycle and timescale threshold for two routes.
# This is a known class of piecewise adaptive congestion dynamics, NOT novelty.
require_relative 'friction_welfare'

module Rithm210AdaptationCycle
  module_function

  def cycle(rho:)
    rho=Rational(rho)
    raise ArgumentError, 'require 0<rho<1' unless rho>0 && rho<1
    lo=(1-rho)/(2-rho)
    hi=1/(2-rho)
    threshold=rho/(2-rho)
    welfare=Rithm210FrictionWelfare.excess_at_zero_bias(x:lo)
    raise 'rational symmetry failed' unless lo+hi==1
    {low:lo,high:hi,critical_kappa:threshold,
     excess_cost_each_period:welfare,
     two_step_contraction:(1-rho)**2}
  end

  def strict_two_cycle?(rho:,kappa:)
    k=Rational(kappa)
    raise ArgumentError,'kappa outside [0,1]' unless k.between?(0,1)
    k < cycle(rho:rho)[:critical_kappa]
  end

  def verify_step(rho:,kappa:)
    z=cycle(rho:rho)
    k=Rational(kappa)
    return false unless strict_two_cycle?(rho:rho,kappa:k)
    low_next=Rithm210FrictionWelfare.step(x:z[:low],k:k,rho:rho)
    high_next=Rithm210FrictionWelfare.step(x:z[:high],k:k,rho:rho)
    low_next==z[:high] && high_next==z[:low]
  end

  # If kappa >= rho, a one-period signal h>kappa causes A->B at x0=1/2,
  # and leaves a post-signal stationary fraction (1-rho)/2.
  # h is a perceived signal in the decision rule, not a travel-time subsidy.
  def one_pulse_lockin(kappa:,rho:,signal:)
    k=Rational(kappa);r=Rational(rho);h=Rational(signal)
    raise ArgumentError,'require 0<rho<=k<=1' unless r>0 && r<=k && k<=1
    raise ArgumentError,'signal must strictly exceed kappa' unless h>k
    z=Rithm210FrictionWelfare.step(x:Rational(1,2),k:k,rho:r,h:h)
    final=Rithm210FrictionWelfare.step(x:z,k:k,rho:r,h:0)
    raise 'no lockin' unless final==z && Rithm210FrictionWelfare.stationary?(x:z,k:k)
    {post_signal_fraction:z,persistent_excess:Rithm210FrictionWelfare.excess_at_zero_bias(x:z)}
  end

  def discounted_tail(excess:,discount:,periods:nil)
    e=Rational(excess);b=Rational(discount)
    raise ArgumentError,'discount in [0,1)' unless b>=0 && b<1
    raise ArgumentError,'excess nonnegative' if e<0
    raise ArgumentError,'periods positive integer' if !periods.nil? &&
      (!periods.is_a?(Integer) || periods<1)
    return e/(1-b) if periods.nil?
    e*(1-b**periods)/(1-b)
  end

  # Joint limit: kappa -> 0, rho=kappa/2, horizon 1/(1-beta)=1/kappa^2.
  # Each-period excess = kappa^2/8, cumulative discounted excess = 1/8.
  def vanishing_friction_long_horizon(kappa:)
    k=Rational(kappa)
    raise ArgumentError,'require 0<kappa<1' unless k>0 && k<1
    rho=k/2
    s=one_pulse_lockin(kappa:k,rho:rho,signal:k+Rational(1,100))
    beta=1-k*k
    {kappa:k,rho:rho,discount:beta,
     flow_excess:s[:persistent_excess],
     infinite_discounted_excess:discounted_tail(
       excess:s[:persistent_excess],discount:beta)}
  end
end

if __FILE__==$PROGRAM_NAME
  require 'json'
  data={cycle:Rithm210AdaptationCycle.cycle(rho:Rational(1,8)),
    pulse:Rithm210AdaptationCycle.one_pulse_lockin(
      kappa:Rational(1,5),rho:Rational(1,8),signal:Rational(2,5)),
    horizon:Rithm210AdaptationCycle.vanishing_friction_long_horizon(kappa:Rational(1,5))}
  puts JSON.pretty_generate(data.transform_values{|item|item.transform_values(&:to_s)})
end
