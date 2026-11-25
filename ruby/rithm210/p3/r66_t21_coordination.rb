# frozen_string_literal: true
# n=5, common opportunity. One of 5 old-A actors uniformly selected.
# Receive move signal with q if selected, f if not; conditional independent delivery.
# All silent A and old B stay; test Bayesian obedience, not forced compliance.
module RithmT21
  module Coordination
    module_function
    def noise(q,f,kappa)
      q,f,k=[q,f,kappa].map { |x| Rational(x) }
      raise ArgumentError,'parameters' unless q.between?(0,1) && f.between?(0,1) && k>=0
      d=q+4*f; received=d>0 ? 4*f+Rational(4*f,d)*(q-f) : nil
      silent=d<5 ? 4*f+Rational(4*(1-f),5-d)*(q-f) : nil
      g_r=received && 1-k-3*received;g_s=silent && 1-k-3*silent;g_b=-4-k+3*d
      {received_gain:g_r,silent_gain:g_s,b_gain:g_b,obedient:(g_r.nil? || g_r>=0) && (g_s.nil? || g_s<=0) && g_b<=0,
       congestion:3*((1-d)**2+q*(1-q)+4*f*(1-f)),switches:d}
    end
    def min_receipt(kappa)
      k=Rational(kappa);raise ArgumentError,'kappa' unless k.between?(0,1)
      Rational(5*(1-k),13-k)
    end
    # B stays; received A moves, silent A mixes at low receipt. q=0 admits
    # the ordinary low symmetric mixed equilibrium; if q>0 and k<1 recipient strict.
    def silent_mix(q,kappa)
      q,k=[q,kappa].map { |x| Rational(x) };raise ArgumentError,'parameters' unless q.between?(0,1) && k.between?(0,1)
      post=Rational(4*q,5-q);r=[0,Rational(1-k-3*post,3*(4-post))].max
      d=q+(5-q)*r
      # selected A moves with q+(1-q)r, four others with r
      x=q+(1-q)*r
      {silent_switch:r,received_gain:1-k-12*r,silent_gain:1-k-3*(4*r+post*(1-r)),b_gain:-4-k+3*d,
       congestion:3*((1-d)**2+x*(1-x)+4*r*(1-r)),switches:d}
    end
    # Clean receipt f=0, obedient branch, n=4 all stay, no erroneous moves.
    def clean_horizon(q,kappa,horizon:40,opportunity:Rational(1,2),resource:0)
      q,k,p,c=[q,kappa,opportunity,resource].map { |x| Rational(x) }
      raise ArgumentError,'parameters' unless q.between?(0,1) && k>=0 && k<=1 && p.between?(0,1) && c>=0 && horizon.is_a?(Integer) && horizon>=1
      raise ArgumentError,'obedience fails' unless noise(q,0,k)[:obedient]
      z=1-p*q
      {congestion:3*(0...horizon).sum { |t| z**t },switches:1-z**(horizon-1),total:3*(0...horizon).sum { |t| z**t }+c*(1-z**(horizon-1))}
    end
  end
end
