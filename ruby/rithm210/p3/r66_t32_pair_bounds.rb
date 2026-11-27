# frozen_string_literal: true
require_relative 'r66_t31_coupling'
module RithmT32
  module PairBounds
    C=RithmT31::Coupling
    module_function
    # Exchangeable five-switch law: uniform subsets conditional on count M.
    # E[M]=5p, E[M(M-1)]=20t, t is the common pair intersection.
    def vertices(p,low,high)
      p,l,h=[p,low,high].map{|x|Rational(x)}
      raise ArgumentError,'pair constraints' unless p.between?(0,1) && 0<=l && l<=h && h<=p
      mu=5*p;out=[];ks=(0..5).to_a
      add=lambda do |support,weights|
        next if weights.any?(&:negative?)
        q=Array.new(6,0);support.zip(weights).each{|k,w|q[k]=w}
        t=q.each_with_index.sum{|w,k|w*k*(k-1)}/20r
        out<<q if t.between?(l,h)
      end
      ks.each{|k|add.call([k],[1]) if mu==k}
      ks.combination(2){|i,j|w=(mu-i)/(j-i);add.call([i,j],[1-w,w])}
      [l,h].uniq.each do |t|
        m2=20*t+mu
        ks.combination(3) do |support|
          w=support.map do |i|
            j,k=support-[i];(m2-(j+k)*mu+j*k)/((i-j)*(i-k))
          end
          add.call(support,w)
        end
      end
      raise ArgumentError,'infeasible pair constraints' if out.empty?
      out.uniq
    end
    def step(q,v,remaining)
      a=q.each_with_index.sum{|w,k|k==0 ? 0 : w*3*(1-k)**2}
      3+q[0]*v+remaining*a
    end
    # Exact rectangular time-varying bounds, not necessarily stationary extrema.
    def bounds(p,low,high,horizon)
      raise ArgumentError,'horizon' unless horizon.is_a?(Integer) && horizon>=1
      vs=vertices(p,low,high);lo=hi=3;lw=[];hw=[]
      (1...horizon).each do |t|
        a=vs.min_by{|q|step(q,lo,t)};b=vs.max_by{|q|step(q,hi,t)}
        lo=step(a,lo,t);hi=step(b,hi,t);lw<<a;hw<<b
      end
      {lower:lo,upper:hi,lower_laws:lw,upper_laws:hw,vertices:vs.size}
    end
    def stationary_range(p,low,high,horizon)
      # Attained vertex witnesses only; not a general stationary upper bound.
      vs=vertices(p,low,high);v=vs.map{|q|[C.absorbing_cost(q,horizon),q]}
      v.minmax_by(&:first)
    end
  end
end
