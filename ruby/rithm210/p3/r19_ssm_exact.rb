# frozen_string_literal: true
# RITHM R19D: exact small-sample model probabilities, prior observations only.
# Reconstructs Appendix B's sampling rules; ties use an explicit fair-coin
# assumption. Not yet original authors' full simulated latent-q likelihood.
module Rithm210R19SSMExact
  module_function
  def distribution(pool,q)
    raise ArgumentError,'q 1..9' unless q.is_a?(Integer)&&q.between?(1,9)
    raise ArgumentError,'nonempty integer reward pool' unless pool.is_a?(Array)&&!pool.empty?&&pool.all?{|v|v.is_a?(Integer)}
    d={0=>1}
    q.times do
      nxt=Hash.new(0)
      d.each{|sum,count|pool.each{|x|nxt[sum+x]+=count}}
      d=nxt
    end
    raise 'sample-count mismatch' unless d.values.sum==pool.size**q
    d
  end
  def informed_probability(differences,q:)
    return 1.to_r/2 if differences.empty?
    hist=distribution(differences,q)
    wins=hist.sum{|sum,count|sum>0 ? count : 0}
    Rational(2*wins+hist.fetch(0,0),2*differences.size**q)
  end
  def uninformed_probability(payoffs_a,payoffs_b,q:)
    return 1.to_r/2 if payoffs_a.empty?||payoffs_b.empty?
    ha=distribution(payoffs_a,q)
    hb=distribution(payoffs_b,q)
    wins=0;ties=0
    ha.each do |a,na|
      hb.each do |b,nb|
        wins+=na*nb if a>b
        ties+=na*nb if a==b
      end
    end
    Rational(2*wins+ties,2*(payoffs_a.size*payoffs_b.size)**q)
  end
  def probability(history:,q:,informed:)
    raise ArgumentError,'history object required' unless history.is_a?(Hash)
    informed ? informed_probability(history.fetch(:paired_differences),q:q) :
      uninformed_probability(history.fetch(:payoffs_a),history.fetch(:payoffs_b),q:q)
  end
  def blank_history
    {paired_differences:[],payoffs_a:[],payoffs_b:[]}
  end
  def append(history:,route_a:,informed:,payoff_tenths:,num_a:nil)
    raise ArgumentError,'binary route' unless [true,false].include?(route_a)
    raise ArgumentError,'integer tenths' unless payoff_tenths.is_a?(Integer)
    if informed
      raise ArgumentError,'informed needs true nA' unless num_a.is_a?(Integer)&&num_a.between?(0,6)
      other_a=num_a-(route_a ? 1 : 0)
      raise ArgumentError,'inconsistent occupancy' unless other_a.between?(0,5)
      history.fetch(:paired_differences)<<10*(11-3*other_a)
    else
      # Never access num_a for uninformed actors.
      history.fetch(route_a ? :payoffs_a : :payoffs_b)<<payoff_tenths
    end
    history
  end
  def prior_mixture(history:,informed:,max_q:9)
    raise ArgumentError,'max q 1..9' unless max_q.is_a?(Integer)&&max_q.between?(1,9)
    (1..max_q).sum{|q|probability(history:history,q:q,informed:informed)}/max_q
  end
end
