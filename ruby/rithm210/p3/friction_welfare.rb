# frozen_string_literal: true
# Exact rational micro-friction -> stationary macro welfare -> pulse memory.
# Two nonatomic parallel links: c_A(x;h)=x+h, c_B(x)=1-x.
# Myopic switchers only move if current alternative cost advantage exceeds k.
module Rithm210FrictionWelfare
  module_function
  def rational(value)
    Rational(value)
  end
  def validate(k:, x:, h: 0)
    k = rational(k); x = rational(x); h = rational(h)
    raise ArgumentError, 'x must be in [0,1]' unless x.between?(0,1)
    raise ArgumentError, 'k must be in [0,1]' unless k.between?(0,1)
    [k,x,h]
  end
  def stationary?(x:, k:, h: 0)
    k,x,h = validate(k:k,x:x,h:h)
    # At x=0 or x=1, absent incumbent types impose no constraint.
    (x == 0 || 2*x + h - 1 <= k) &&
      (x == 1 || 1 - 2*x - h <= k)
  end
  def interior_stationary_band(k:,h:0)
    k = rational(k); h = rational(h)
    raise ArgumentError, 'k must be in [0,1]' unless k.between?(0,1)
    [Rational(1,2)*(1-h-k), Rational(1,2)*(1-h+k)]
  end
  def social_cost(x:,h:0)
    x=rational(x);h=rational(h)
    raise ArgumentError,'x out of range' unless x.between?(0,1)
    x*(x+h)+(1-x)*(1-x)
  end
  def excess_at_zero_bias(x:)
    social_cost(x:x)-Rational(1,2)
  end
  def inertia_bound(k:)
    k=rational(k)
    raise ArgumentError,'k out of range' unless k.between?(0,1)
    k*k/2
  end
  def step(x:, k:, rho:, h:0)
    k,x,h=validate(k:k,x:x,h:h);rho=rational(rho)
    raise ArgumentError,'rho must lie in [0,1]' unless rho.between?(0,1)
    gap=2*x+h-1
    if gap>k
      x-rho*x # share rho of A users changes to B
    elsif gap< -k
      x+rho*(1-x) # share rho of B users changes to A
    else
      x
    end
  end
  def pulse_example
    k=Rational(1,5);rho=Rational(1,8);start=Rational(1,2)
    pulse=step(x:start,k:k,rho:rho,h:Rational(2,5))
    after=step(x:pulse,k:k,rho:rho,h:0)
    baseline=step(x:start,k:k,rho:rho,h:0)
    {k:k,rho:rho,start:start,after_pulse:pulse,after_return:after,
      no_pulse:baseline,stationary_after_return:stationary?(x:after,k:k),
      pulse_path_cost:social_cost(x:after),no_pulse_path_cost:social_cost(x:baseline),
      persistent_welfare_excess:social_cost(x:after)-social_cost(x:baseline)}
  end
end
if __FILE__==$PROGRAM_NAME
 require 'json'
 out=Rithm210FrictionWelfare.pulse_example
 puts JSON.pretty_generate(out.transform_values { |x| x.is_a?(Rational) ? {fraction:x.to_s,decimal:x.to_f} : x })
end
