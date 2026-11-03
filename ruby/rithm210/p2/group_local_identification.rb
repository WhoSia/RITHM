# frozen_string_literal: true
# P2-R3 exact group-local common-shock counterexample, Rational arithmetic.
module Rithm210GroupLocalIdentification
  module_function
  def choose(n,k)
    return 0 unless k.between?(0,n)
    (1..k).reduce(1){|v,j|v*(n-j+1)/j}
  end
  def binomial(n,k,q)
    choose(n,k)*q**k*(1-q)**(n-k)
  end
  def group_law(a:,p:,delta:)
    raise ArgumentError,'group size' unless a.is_a?(Integer) && a.between?(0,6)
    raise ArgumentError,'probabilities' unless delta>=0 && p-delta>=0 && p+delta<=1
    b=6-a
    (0..b).flat_map do |u|
      (0..a).map do |d|
        [[u,d],(binomial(b,u,p+delta)*binomial(a,d,p+delta)+
                  binomial(b,u,p-delta)*binomial(a,d,p-delta))/2]
      end
    end.to_h
  end
  def directed_law(a:,p:,delta:)
    law=group_law(a:a,p:p,delta:delta)
    marginal=Hash.new(0)
    law.each{|(u,_),v|marginal[u]+=v}
    law.to_h{|(u,d),v|[[u,d],marginal.fetch(u)*v/marginal.fetch(u)]}
  end
  def latent_do_d_mean(a:,p:,delta:,u:)
    raise ArgumentError,'u out of support' unless u.between?(0,6-a)
    a*p
  end
  def directed_do_d_mean(a:,p:,delta:,u:)
    law=group_law(a:a,p:p,delta:delta)
    denom=law.select{|(uu,_),_|uu==u}.values.sum
    raise ArgumentError,'zero marginal' if denom==0
    law.sum{|(uu,d),v|uu==u ? d*v : 0}/denom
  end
  # Independent hidden state in each group: between-group residual moment is zero.
  def predicted_moments(a:,p:,delta:)
    {within:a*(6-a)*delta**2,between:0}
  end
  def two_group_law(a:,p:,delta:)
    single=group_law(a:a,p:p,delta:delta)
    single.flat_map{|k,v|single.map{|l,w|[[k,l],v*w]}}.to_h
  end
end
