# frozen_string_literal: true
# RITHM R18-P2: exploit the exact sign symmetry of a balanced four-arm
# interaction under the FISHER SHARP NULL. Not a general weak-null test.
require_relative 'r18_randomization_inference'
module Rithm210R18SignReduction
  module_function
  R=Rithm210R18RandomizationInference
  def choose(n,k)
    raise ArgumentError,'choose integers 0<=k<=n' unless [n,k].all?{|x|x.is_a?(Integer)} && k>=0 && n>=k
    (1..[k,n-k].min).reduce(1){|acc,j|acc*(n-[k,n-k].min+j)/j}
  end
  def minimum_two_sided_p(n)
    raise ArgumentError,'four balanced arms' unless n.is_a?(Integer) && n>=4 && n%4==0
    2.0/choose(n,n/2)
  end
  def exact_sharp_null(assignment,outcome,max_sessions:16)
    m=R.validate(assignment,outcome)
    ids=assignment.keys
    raise ArgumentError,'too many clusters to enumerate' unless ids.size<=max_sessions
    observed=R.estimate(assignment,outcome)[:interaction]
    ys=ids.map{|id|outcome.fetch(id).to_f}
    total=ys.sum
    n=ids.length
    positives=n/2
    hits=0;reps=0
    (0...n).to_a.combination(positives) do |ix|
      signed=(2.0*ix.sum{|i|ys.fetch(i)}-total)/m
      hits+=1 if signed.abs>=observed.abs-1e-10
      reps+=1
    end
    raise 'unexpected sign combinations' unless reps==choose(n,positives)
    {observed:observed,p_two_sided:hits.to_f/reps,assignments:reps,
     method:'exact sign-reduced Fisher sharp-null',per_arm:m,
     min_resolution:minimum_two_sided_p(n)}
  end
end
