# frozen_string_literal: true
require_relative 'r66_t22_identification'
module RithmT23
  module MonotoneProxy
    I=RithmT22::Identification
    module_function
    # Z independent of outcome given E; P(Z=1|E=1)>=P(Z=1|E=0).
    # No restriction on inactive transition or positive q other than q<=1.
    def bounds(j0,j1,route)
      a,b=[j0,j1].map{|r|r.map{|x|Rational(x)}}
      raise ArgumentError,'joint rows/route' unless [a,b].all?{|r|r.size==6 && r.all?{|x|x>=0}} && a.sum+b.sum==1 && [:a,:b].include?(route)
      m=b.sum;p=a.zip(b).map(&:sum)
      if m==0 || m==1 || a.zip(b).all?{|x,y|m*x==(1-m)*y}
        witnesses=(0..5).filter_map do |k|
          q=p[k];next if q==0
          active=Array.new(6){|j|j==k ? 1 : 0};inactive=q==1 ? active : p.zip(active).map{|x,y|(x-q*y)/(1-q)}
          {active:active,inactive:inactive,q:q,alpha:m,beta:m}
        end
      else
        r0=a.map{|v|v/(1-m)};r1=b.map{|v|v/m};d=r1.zip(r0).map{|x,y|x-y}
        cap=(0..5).filter_map{|k| -r0[k]/d[k] if d[k]<0}.min
        # Endpoints of the feasible extension beyond the tagged conditional row.
        witnesses=[1,cap].map do |z|
          q=m/z;active=r0.zip(d).map{|x,y|x+z*y}
          {active:active,inactive:r0,q:q,alpha:1,beta:(m-q)/(1-q)}
        end
      end
      witnesses.each{|x|x[:gain]=I.gain(x[:active],route)}
      low,high=witnesses.minmax_by{|x|x[:gain]}
      {low:low[:gain],high:high[:gain],low_witness:low,high_witness:high}
    end
  end
end
