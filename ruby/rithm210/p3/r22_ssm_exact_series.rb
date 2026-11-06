# frozen_string_literal: true
# Exact q-series using independent differences, not separate A/B sum kernels.
# For uninformed SSM with independent WITH-replacement draws:
# sum(A_k)-sum(B_k) has same law as sum(A_k-B_k).
module Rithm210R22SSMExactSeries
  module_function
  def series_from_pool(pool,qmax:9)
    raise ArgumentError,'qmax 1..9' unless qmax.is_a?(Integer)&&qmax.between?(1,9)
    raise ArgumentError,'nonempty integer pool' unless pool.is_a?(Array)&&!pool.empty?&&pool.all?{|x|x.is_a?(Integer)}
    hist=pool.tally
    distribution={0=>1};den=1;answers=[]
    qmax.times do
      nxt=Hash.new(0)
      distribution.each{|s,n|hist.each{|v,count|nxt[s+v]+=n*count}}
      den*=pool.length
      raise 'mass mismatch' unless nxt.values.sum==den
      wins=nxt.sum{|v,n|v.positive? ? n : 0}
      answers<<Rational(2*wins+nxt.fetch(0,0),2*den)
      distribution=nxt
    end
    answers
  end
  def probabilities(history:,informed:,qmax:9)
    raise ArgumentError,'history hash' unless history.is_a?(Hash)
    raise ArgumentError,'information boolean' unless [true,false].include?(informed)
    raise ArgumentError,'qmax 1..9' unless qmax.is_a?(Integer)&&qmax.between?(1,9)
    pool=if informed
      history.fetch(:paired_differences)
    else
      a=history.fetch(:payoffs_a);b=history.fetch(:payoffs_b)
      a.empty?||b.empty? ? [] : a.product(b).map{|x,y|x-y}
    end
    return Array.new(qmax,Rational(1,2)) if pool.empty?
    series_from_pool(pool,qmax:qmax)
  end
end
