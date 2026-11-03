# frozen_string_literal: true
# Exact finite observational equivalence; Rational arithmetic, no dependencies.
module Rithm210JointEquivalence
  module_function
  def choose(n,k)
    return 0 unless k.between?(0,n)
    (1..k).reduce(1){|r,i|r*(n-i+1)/i}
  end
  def binomial(n,k,p)
    choose(n,k)*p**k*(1-p)**(n-k)
  end
  def joint(a:,p:,delta:)
    raise ArgumentError,'a' unless a.is_a?(Integer) && a.between?(0,6)
    raise ArgumentError,'probability' unless p-delta>=0 && p+delta<=1
    b=6-a
    (0..b).flat_map do |u|
      (0..a).map do |d|
        q=((binomial(b,u,p+delta)*binomial(a,d,p+delta))+
           (binomial(b,u,p-delta)*binomial(a,d,p-delta)))/2
        [[u,d],q]
      end
    end.to_h
  end
  def direct_chain(a:,p:,delta:)
    tab=joint(a:a,p:p,delta:delta)
    marg=Hash.new(0)
    tab.each{|(u,_d),v|marg[u]+=v}
    tab.to_h{|(u,d),v|[[u,d],marg[u]*(v/marg[u])]} # U -> D by inverse-CDF sampler.
  end
  def dependent_conditional_d(a:,p:,delta:,u:)
    b=6-a
    probs=[p+delta,p-delta]
    w=probs.map{|q|binomial(b,u,q)/2}
    z=w.sum
    raise ArgumentError,'zero marginal' if z==0
    (0..a).map{|d| w.each_with_index.sum{|weight,i| weight*binomial(a,d,probs[i])}/z}
  end
  def do_d_mean_latent(a:,p:,delta:,u:)
    a*p # intervention on U does not affect shared Z or D
  end
  def do_d_mean_direct(a:,p:,delta:,u:)
    dependent_conditional_d(a:a,p:p,delta:delta,u:u).each_with_index.sum{|prob,d|prob*d}
  end
end
