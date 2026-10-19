# frozen_string_literal: true
require 'json'
module RouteCostCourt
  module_function
  def congestion(bits)
    raise ArgumentError, 'binary routes required' unless bits.is_a?(Array) && !bits.empty? && bits.all? { |x| x == 0 || x == 1 }
    a=bits.count(0); b=bits.length-a
    a*a+b*b
  end
  def mismatch(truth, forecast)
    raise ArgumentError, 'different cohort' unless truth.length == forecast.length
    truth.zip(forecast).count { |x,y| x != y }
  end
  def assess(truth, better, worse)
    raise ArgumentError, 'no strictly better individual forecast' unless mismatch(truth,better)<mismatch(truth,worse)
    da=(congestion(truth)-congestion(better)).abs
    db=(congestion(truth)-congestion(worse)).abs
    { 'truth'=>truth, 'individual_better'=>better,'individual_worse'=>worse,
      'better_hamming'=>mismatch(truth,better),'worse_hamming'=>mismatch(truth,worse),
      'truth_cost'=>congestion(truth),'better_cost'=>congestion(better),'worse_cost'=>congestion(worse),
      'better_cost_error'=>da,'worse_cost_error'=>db,'cost_rank_reversed'=>da>db }
  end
  def vectors(n)
    (0...(1<<n)).map {|mask| Array.new(n) {|i| (mask >> (n-i-1)) & 1}}
  end
  def census(n)
    raise ArgumentError,'bounded exhaustive court 2..5' unless (2..5).cover?(n)
    all=vectors(n); pairs=0; reversals=0; equal_cost=0; witness=nil
    all.each do |truth|
      all.each do |a|
        all.each do |b|
          next unless mismatch(truth,a)<mismatch(truth,b)
          pairs+=1
          r=assess(truth,a,b)
          reversals+=1 if r.fetch('cost_rank_reversed')
          equal_cost+=1 if r.fetch('better_cost_error')==r.fetch('worse_cost_error')
          witness||=r if r.fetch('cost_rank_reversed')
        end
      end
    end
    {'cohort'=>n,'compared_strict_pairs'=>pairs,'rank_reversals'=>reversals,
     'tied_cost_errors'=>equal_cost,'first_witness'=>witness,'source'=>'synthetic exhaustive binary assignments',
     'causal_effect_identified'=>false}
  end
end
if $PROGRAM_NAME == __FILE__
  n=Integer(ARGV.fetch(0,'3'))
  puts JSON.pretty_generate(RouteCostCourt.census(n))
end
