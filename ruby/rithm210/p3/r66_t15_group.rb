# frozen_string_literal: true
require_relative 'r66_t15_spell'
require_relative 'r66_t12_schedules'
module RithmT15
  module Group
    module_function
    S=RithmT12::Schedules
    CLOCKS=[:common,:independent,:fixed_three].freeze
    # state = [A slow,A fast,B slow,B fast]. All actors exchangeable within type/route.
    def binom(n,p,k)
      return 0 unless k.between?(0,n)
      S.choose(n,k)*p**k*(1-p)**(n-k)
    end
    def initial(n)
      raise ArgumentError,'n' unless n.is_a?(Integer) && n.between?(0,6)
      (0..n).flat_map { |a| (0..6-n).map { |b| [[a,n-a,b,6-n-b],Rational(S.choose(n,a)*S.choose(6-n,b),64)] } }.to_h
    end
    def activation(l,h,clock)
      raise ArgumentError,'clock' unless CLOCKS.include?(clock)
      return {[0,0]=>Rational(1,2),[l,h]=>Rational(1,2)}.tap { |x| x[[0,0]]=1 if l+h==0 } if clock==:common
      out={}
      (0..l).each do |i|
        (0..h).each do |j|
          p=clock==:independent ? Rational(S.choose(l,i)*S.choose(h,j),2**(l+h)) : Rational(S.choose(l,i)*S.choose(h,j)*S.choose(6-l-h,3-i-j),20)
          out[[i,j]]=p unless p.zero?
        end
      end
      out
    end
    def row(state,clock,mechanism,reset_probability: nil)
      raise ArgumentError,'state' unless state.length==4 && state.all? { |x| x.is_a?(Integer) && x>=0 } && state.sum==6
      raise ArgumentError,'mechanism' unless [:fixed,:reset,:partial].include?(mechanism)
      r=Rational(reset_probability || (mechanism==:reset ? 1 : 0))
      raise ArgumentError,'reset probability' unless r.between?(0,1) && (mechanism==:partial || r==(mechanism==:reset ? 1 : 0))
      raise ArgumentError,'clock' unless CLOCKS.include?(clock)
      n=state[0]+state[1]
      return {state=>Rational(1)} if n==4
      from=n>4 ? 0 : 2; to=2-from
      out=Hash.new(0)
      activation(state[from],state[from+1],clock).each do |(i,j),w|
        (0..i).each do |d|
          (0..j).each do |u|
            p=w*binom(i,Spell::P[0],d)*binom(j,Spell::P[1],u)
            k=d+u
            draw=Hash.new(0)
            (0..d).each do |a|
              (0..u).each do |b|
                draw[a+b]+=binom(d,1-r/2,a)*binom(u,r/2,b)
              end
            end
            draw.each do |a,q|
              next if (p*q).zero?
              z=state.dup;z[from]-=d;z[from+1]-=u;z[to]+=a;z[to+1]+=k-a
              out[z]+=p*q
            end
          end
        end
      end
      raise 'mass leak' unless out.values.sum==1
      out
    end
    def occupancy(dist)
      out=Array.new(7,0);dist.each { |s,p| out[s[0]+s[1]]+=p };out
    end
    def forecast(n:,horizon:,clock:,mechanism:,reset_probability: nil)
      raise ArgumentError,'horizon' unless horizon.is_a?(Integer) && horizon>=1
      d=initial(n); cache={};cost=0
      horizon.times do |t|
        cost+=d.sum { |s,p| p*3*(s[0]+s[1]-4)**2 }
        next if t==horizon-1
        next_d=Hash.new(0)
        d.each do |s,p|
          (cache[s]||=row(s,clock,mechanism,reset_probability: reset_probability)).each { |z,q| next_d[z]+=p*q }
        end
        d=next_d
      end
      raise 'mass leak' unless d.values.sum==1
      {congestion:cost,final:occupancy(d)}
    end
  end
end
