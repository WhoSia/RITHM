# frozen_string_literal: true
# Rational finite-state transient Markov analysis under an oracle opponent snapshot.
# This does NOT reproduce the actual laboratory players' private information sets.
require_relative 'adjustment_clocks'
module Rithm210MixedClockChain
  module_function
  STATES = [0, 1, 2, 3, 5, 6].freeze
  def probability(x, name)
    v=Rational(x)
    raise ArgumentError,"#{name} outside [0,1]" unless v.between?(0,1)
    v
  end
  def transition(n,sync:)
    Rithm210AtomicNash.group_cost(n)
    s=probability(sync,:sync)
    row=Hash.new(0)
    row[Rithm210AdjustmentClocks.synchronous(n)]+=s
    if n<4
      row[n+1]+=(1-s)*Rational(6-n,6)
      row[n]+=(1-s)*Rational(n,6)
    elsif n>4
      row[n-1]+=(1-s)*Rational(n,6)
      row[n]+=(1-s)*Rational(6-n,6)
    else
      row[4]+=(1-s)
    end
    raise 'non-stochastic transition' unless row.values.sum==1 && row.values.all?{|p|p>=0}
    row
  end
  def linear_solve(matrix,vector)
    n=vector.size
    raise ArgumentError,'non-square' unless matrix.size==n && matrix.all?{|row|row.size==n}
    a=Array.new(n){|i|matrix[i].map{|v|Rational(v)}+[Rational(vector[i])]}
    n.times do |j|
      p=(j...n).find{|i|a[i][j]!=0}
      raise ArgumentError,'singular system' if p.nil?
      a[j],a[p]=a[p],a[j] if p!=j
      pivot=a[j][j]
      (j..n).each{|k|a[j][k]/=pivot}
      n.times do |i|
        next if i==j
        factor=a[i][j]
        next if factor==0
        (j..n).each{|k|a[i][k]-=factor*a[j][k]}
      end
    end
    a.map(&:last)
  end
  def value_vector(sync:,discount:,reward:)
    s=probability(sync,:sync)
    b=probability(discount,:discount)
    raise ArgumentError,'discount must be less than 1' if b==1
    matrix=STATES.map do |n|
      row=transition(n,sync:s)
      STATES.map{|m|Rational(n==m ? 1 : 0)-b*row.fetch(m,0)}
    end
    vector=STATES.map{|n|reward.fetch(n)}
    STATES.zip(linear_solve(matrix,vector)).to_h.merge(4=>0)
  end
  def discounted_excess(sync:,discount:)
    rewards=STATES.to_h{|n|[n,Rithm210AtomicNash.group_cost(n)-24]}
    value_vector(sync:sync,discount:discount,reward:rewards)
  end
  def expected_hitting_times(sync:)
    s=probability(sync,:sync)
    raise ArgumentError,'no absorption at full synchronization from nonoptimal states' if s==1
    matrix=STATES.map do |n|
      row=transition(n,sync:s)
      STATES.map{|m|Rational(n==m ? 1 : 0)-row.fetch(m,0)}
    end
    STATES.zip(linear_solve(matrix,Array.new(STATES.size,1))).to_h.merge(4=>0)
  end
  def finite_horizon(sync:,start:,horizon:)
    raise ArgumentError,'horizon must be nonnegative integer' unless horizon.is_a?(Integer)&&horizon>=0
    Rithm210AtomicNash.group_cost(start)
    distribution={start=>Rational(1)}
    rows=[]
    (0...horizon).each do |t|
      loss=distribution.sum{|n,p|p*(Rithm210AtomicNash.group_cost(n)-24)}
      rows << {period:t,prob_optimum:distribution.fetch(4,0),expected_excess:loss}
      newer=Hash.new(0)
      distribution.each{|n,p|transition(n,sync:sync).each{|m,q|newer[m]+=p*q}}
      distribution=newer
    end
    rows
  end
end
