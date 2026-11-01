# frozen_string_literal: true
# Exploratory sensitivity and paired whole-session bootstrap for 5616 group transitions.
require_relative 'empirical_group_baseline'
require 'json'
module RithmBaselineRobustness
 module_function
 def interval(session_rows,head,draws:20_000,seed:20261101)
  rng=Random.new(seed); n=session_rows.size
  delta=->(a,weighted) {
    a.sum { |r| (weighted ? r[:n] : 1) * (r['conditional'][head]-r['global'][head]) } /
      a.sum { |r| weighted ? r[:n] : 1 }.to_f
  }
  {equal_session:false,transition_weighted:true}.to_h do |label,weighted|
    boot=Array.new(draws) {
      sample=Array.new(n){session_rows.fetch(rng.rand(n))}
      delta.call(sample,weighted)
    }.sort
    [label,{point:delta.call(session_rows,weighted),
      lower:boot[(0.025*draws).floor],upper:boot[(0.975*draws).floor]}]
  end
 end
 def run(input)
  sensitivity=[1,5,20,100].map do |alpha|
    result=RithmEmpiricalBaseline.evaluate(input,alpha:alpha)
    {alpha:alpha,pooled:result[:pooled]}
  end
  baseline=RithmEmpiricalBaseline.evaluate(input,alpha:20.0)
  {sensitivity:sensitivity,bootstrap:{
    joint:interval(baseline[:session_rows],:joint),
    count:interval(baseline[:session_rows],:count)}}
 end
end
puts JSON.pretty_generate(RithmBaselineRobustness.run(ARGV.fetch(0))) if $PROGRAM_NAME == __FILE__
