# frozen_string_literal: true
# Numeric acceleration: identical iid sampling LAW to exact rational engine,
# but double precision arithmetic; verify against rational series before use.
module Rithm210R22SSMFloatSeries
  module_function
  def probabilities(history:,informed:,qmax:9)
    raise ArgumentError,'qmax' unless qmax.is_a?(Integer)&&qmax.between?(1,9)
    raise ArgumentError,'information boolean' unless [true,false].include?(informed)
    if informed
      pool=history.fetch(:paired_differences)
      frequencies=pool.tally
      denom=pool.length
    else
      a=history.fetch(:payoffs_a).tally
      b=history.fetch(:payoffs_b).tally
      frequencies=Hash.new(0)
      a.each{|va,ca|b.each{|vb,cb|frequencies[va-vb]+=ca*cb}}
      denom=history.fetch(:payoffs_a).length*history.fetch(:payoffs_b).length
    end
    return Array.new(qmax,0.5) if denom.zero?
    raise 'source pool mass mismatch' unless frequencies.values.sum==denom
    weighted=frequencies.map{|x,n|[x,n.to_f/denom]}
    state={0=>1.0};answers=[]
    qmax.times do
      nxt=Hash.new(0.0)
      state.each{|sum,p|weighted.each{|x,w|nxt[sum+x]+=p*w}}
      answers << nxt.sum{|value,p|value>0 ? p : (value==0 ? p/2.0 : 0.0)}
      state=nxt
    end
    answers
  end
end
