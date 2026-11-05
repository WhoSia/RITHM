# frozen_string_literal: true
# RITHM-2.10 P3-R19: sharp finite-horizon welfare envelope over
# labeled six-agent states consistent with an observed occupancy.
# Fixed, known actor-specific switch laws, not empirically identified.
module Rithm210R19PartialWelfare
  module_function
  N = 6
  STATES = 1 << N
  def occupancy(mask)
    raise ArgumentError, 'invalid mask' unless mask.is_a?(Integer) && mask.between?(0, 63)
    mask.digits(2).sum
  end
  def cost(mask)
    n = occupancy(mask)
    n*n + 2*(N-n)**2
  end
  def validate_probabilities(probs)
    raise ArgumentError, 'six rational probabilities required' unless
      probs.is_a?(Array) && probs.size==N &&
      probs.all? { |p| p.is_a?(Rational) && p.between?(0,1) }
    true
  end
  def kernel(p_a:,p_b:)
    validate_probabilities(p_a)
    validate_probabilities(p_b)
    Array.new(STATES) do |mask|
      out={mask=>1.to_r}
      N.times do |i|
        prob=(mask & (1<<i)).zero? ? p_b[i] : p_a[i]
        nxt=Hash.new(0.to_r)
        out.each do |state,mass|
          nxt[state]+=mass*(1-prob)
          nxt[state^(1<<i)]+=mass*prob
        end
        out=nxt
      end
      raise 'transition mass lost' unless out.values.sum==1
      out
    end
  end
  def values(p_a:,p_b:,horizon:)
    raise ArgumentError, 'positive integer horizon' unless horizon.is_a?(Integer)&&horizon.positive?
    k=kernel(p_a:p_a,p_b:p_b)
    v=Array.new(STATES){|m|cost(m).to_r}
    (horizon-1).times do
      previous=v
      v=Array.new(STATES){|m| cost(m).to_r + k[m].sum{|dest,pr|pr*previous[dest]}}
    end
    v
  end
  def envelope(observed_n:,p_a:,p_b:,horizon:)
    raise ArgumentError,'observed occupancy 0..6 required' unless observed_n.is_a?(Integer)&&observed_n.between?(0,N)
    v=values(p_a:p_a,p_b:p_b,horizon:horizon)
    states=(0...STATES).select{|m|occupancy(m)==observed_n}
    lo=states.min_by{|m|[v[m],m]}
    hi=states.max_by{|m|[v[m],-m]}
    {n:observed_n,horizon:horizon,compositions:states.size,
     minimum:v[lo],maximum:v[hi],width:v[hi]-v[lo],
     minimizer:lo,maximizer:hi,sharp:true}
  end
  def toggle_actor_zero
    a=Array.new(N,0.to_r)
    a[0]=1.to_r
    [a,a.dup]
  end
  def counterexample(horizon:40)
    a,b=toggle_actor_zero
    treated=envelope(observed_n:3,p_a:a,p_b:b,horizon:horizon)
    untreated=envelope(observed_n:3,p_a:Array.new(N,0.to_r),
      p_b:Array.new(N,0.to_r),horizon:horizon)
    {baseline:untreated,intervention:treated,
     treatment_effect_range:[treated[:minimum]-untreated[:maximum],
       treated[:maximum]-untreated[:minimum]],
     interpretation:'Sharp aggregate-only partial identification under fixed known actor-switch laws; not a new empirical treatment effect.'}
  end
end
if __FILE__==$PROGRAM_NAME
  require 'json'
  puts JSON.pretty_generate(Rithm210R19PartialWelfare.counterexample)
end
