# frozen_string_literal: true
require_relative 'r66_t16_belief'
require_relative 'r66_t12_schedules'
module RithmT17
  module Oracle
    module_function
    B=RithmT16::Belief; S=RithmT12::Schedules
    def schedule(clock)
      case clock
      when :common then S.common
      when :independent then S.independent
      when :fixed_three then S.fixed_count(3)
      else raise ArgumentError,'clock'
      end
    end
    def probability(x)
      q=Rational(x); raise ArgumentError,'probability' unless q.between?(0,1);q
    end
    # Each of ten unit travel-value intervals has mass 1/10 and constant posterior support.
    def flip(k,route,rho:,disclosure:,response:,threshold:0)
      rho,disclosure,response=[rho,disclosure,response].map { |x| probability(x) }
      base=B.binomial_base; c=Rational(threshold);raise ArgumentError,'threshold' if c<0
      decide=->(p) { B.expected_gain(B.predict(p,persistence:rho,base:base),route)>c ? 1 : 0 }
      perfect=decide.call(B::STATES.map { |j| j==k ? 1 : 0 })
      partial=(0...10).sum do |i|
        y=Rational(13+2*i,2)-B.cost(k,route)
        decide.call(B.posterior(base,route,y))
      end
      response*(disclosure*perfect+(1-disclosure)*Rational(partial,10))
    end
    # Independent labelled flips conditional on a common eligibility mask and old occupancy.
    def row(n,clock:,**params)
      raise ArgumentError,'occupancy' unless n.is_a?(Integer) && n.between?(0,6)
      rates=[n>0 ? flip(n-1,:a,**params) : 0,n<6 ? flip(n,:b,**params) : 0]
      result=Array.new(7,Rational(0))
      schedule(clock).each_with_index do |w,mask|
        next if w.zero?
        64.times do |moves|
          next unless (moves & ~mask).zero?
          p=w; next_n=n
          6.times do |i|
            next if (mask & (1<<i)).zero?
            a=i<n;rate=rates[a ? 0 : 1]
            if (moves & (1<<i)).zero?
              p*=1-rate
            else
              p*=rate;next_n+=a ? -1 : 1
            end
          end
          result[next_n]+=p
        end
      end
      raise 'mass' unless result.sum==1
      result.freeze
    end
    # Under full disclosure posterior resets to a point every round: exact Markov chain.
    def full_forecast(n:,horizon:,clock:,rho:,response:,threshold:0)
      raise ArgumentError,'horizon/state' unless horizon.is_a?(Integer) && horizon>=1 && n.is_a?(Integer) && n.between?(0,6)
      p=(0..6).map { |k| row(k,clock:clock,rho:rho,disclosure:1,response:response,threshold:threshold) }
      d=Array.new(7,0);d[n]=1;total=0
      horizon.times do |t|
        total+=d.each_with_index.sum { |v,k| v*3*(k-4)**2 }
        next if t==horizon-1
        d=(0..6).map { |j| (0..6).sum { |k| d[k]*p[k][j] } }
      end
      {cost:total,final:d}
    end
  end
end
