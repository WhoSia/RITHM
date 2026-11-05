# frozen_string_literal: true
# RITHM 2.10 R16: exact finite-state independent-switch welfare benchmark.
# A mathematical negative-control, not an empirical learner or novel theorem.
module Rithm210FiniteHorizonIndependentWelfare
  N=6
  module_function
  def rate(x)
    q=Rational(x)
    raise ArgumentError,'probability must lie in [0,1]' unless q.between?(0,1)
    q
  end
  def binomial(n,k,p)
    return 0.to_r unless k.between?(0,n)
    choose=(1..k).reduce(1){|v,j|v*(n-k+j)/j}
    choose*p**k*(1-p)**(n-k)
  end
  def kernel(a:,b:)
    a=rate(a);b=rate(b)
    (0..N).map do |n|
      row=Array.new(N+1,0.to_r)
      (0..n).each do |d|
        (0..(N-n)).each do |u|
          row[n+u-d]+=binomial(n,d,a)*binomial(N-n,u,b)
        end
      end
      raise 'transition row does not sum to one' unless row.sum==1
      row
    end
  end
  def next_distribution(dist,k)
    raise ArgumentError,'distribution must have 7 states and unit mass' unless dist.size==N+1 && dist.sum==1
    (0..N).map{|j|(0..N).sum{|i|dist[i]*k[i][j]}}
  end
  def cost(n)
    raise ArgumentError,'n must be 0..6' unless (0..N).cover?(n)
    n*n+2*(N-n)**2
  end
  def expected_excess(dist)
    (0..N).sum{|n|dist[n]*(cost(n)-24)}
  end
  def moments(dist)
    mean=(0..N).sum{|n|dist[n]*n}
    variance=(0..N).sum{|n|dist[n]*(n-mean)**2}
    {mean:mean,variance:variance,excess:expected_excess(dist)}
  end
  def run(a:,b:,start:4,horizon:40,discount:1)
    raise ArgumentError,'invalid initial n or horizon' unless (0..N).cover?(start) && horizon.positive?
    beta=rate(discount);k=kernel(a:a,b:b)
    dist=Array.new(N+1,0.to_r);dist[start]=1.to_r
    path=[];total=0.to_r
    horizon.times do |t|
      entry=moments(dist)
      raise 'quadratic welfare identity failed' unless entry[:excess]==3*(entry[:variance]+(entry[:mean]-4)**2)
      path<<entry.merge(period:t)
      total+=beta**t*entry[:excess]
      dist=next_distribution(dist,k)
    end
    {a:rate(a),b:rate(b),initial:start,horizon:horizon,discount:beta,
     cumulative_discounted_excess:total,path:path,terminal_distribution:dist}
  end
  def same_stationary_mean_comparison(horizon:40)
    slow=run(a:Rational(1,10),b:Rational(1,5),horizon:horizon)
    fast=run(a:Rational(1,4),b:Rational(1,2),horizon:horizon)
    raise 'stationary share mismatch' unless slow[:b]/(slow[:a]+slow[:b])==fast[:b]/(fast[:a]+fast[:b])
    {slow:slow[:cumulative_discounted_excess],fast:fast[:cumulative_discounted_excess],
     difference:fast[:cumulative_discounted_excess]-slow[:cumulative_discounted_excess],
     one_step_slow:slow[:path][1],one_step_fast:fast[:path][1]}
  end
end
if __FILE__==$PROGRAM_NAME
 require 'json'
 out=Rithm210FiniteHorizonIndependentWelfare.same_stationary_mean_comparison
 puts JSON.pretty_generate(out.transform_values{|x|x.is_a?(Hash) ? x.transform_values{|v|v.is_a?(Rational) ? v.to_f : v} : x.to_f})
end
