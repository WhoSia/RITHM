# frozen_string_literal: true
require_relative 'r66_t12_schedules'

module RithmT12
  module Kernel
    module_function
    def route_cost(n)
      raise ArgumentError,'route-A occupants in 0..6' unless n.is_a?(Integer) && n.between?(0,6)
      3*(n-4)**2
    end
    # Toy revision rates inherited from R66-T5, NOT human-fitted parameters.
    def revision_rates(n)
      route_cost(n)
      [3*n-14>0 ? Rational(2,5) : Rational(1,50),
       11-3*n>0 ? Rational(2,5) : Rational(1,50)]
    end
    def coin(n,p,k)
      return Rational(0) unless k.between?(0,n)
      Rational(Schedules.choose(n,k))*p**k*(1-p)**(n-k)
    end
    def masked_row(n,active_mask,effort=Rational(1))
      route_cost(n)
      effort=Rational(effort)
      raise ArgumentError,'effort in 0..1' unless effort.between?(0,1)
      a,b=revision_rates(n)
      na=(0...n).count { |i| (active_mask&(1<<i))!=0 }
      nb=(n...6).count { |i| (active_mask&(1<<i))!=0 }
      law=Array.new(7,Rational(0))
      (0..na).each do |down|
        (0..nb).each do |up|
          law[n-down+up]+=coin(na,a*effort,down)*coin(nb,b*effort,up)
        end
      end
      raise 'probability row invalid' unless law.sum == 1
      [law.freeze,na*a*effort+nb*b*effort]
    end
    def transition(schedule,effort=Rational(1))
      weights=Schedules.validate(schedule)
      rows=[];gross=[]
      7.times do |n|
        law=Array.new(7,Rational(0));moves=Rational(0)
        weights.each_with_index do |w,mask|
          next if w.zero?
          row,flips=masked_row(n,mask,effort)
          row.each_with_index { |prob,j| law[j]+=w*prob }
          moves+=w*flips
        end
        raise 'transition mass violation' unless law.sum == 1
        rows << law.freeze;gross << moves
      end
      [rows.freeze,gross.freeze]
    end
    def forecast(n0:,horizon:,schedule:,effort:Rational(1),fee:Rational(0))
      route_cost(n0)
      raise ArgumentError,'positive integer horizon' unless horizon.is_a?(Integer) && horizon.positive?
      fee=Rational(fee)
      raise ArgumentError,'nonnegative real resource fee required' if fee.negative?
      p,switches=transition(schedule,effort)
      dist=Array.new(7,Rational(0));dist[n0]=Rational(1)
      congestion=Rational(0);moves=Rational(0)
      horizon.times do |t|
        congestion+=7.times.sum(Rational(0)) { |n| dist[n]*route_cost(n) }
        next if t==horizon-1
        moves+=7.times.sum(Rational(0)) { |n| dist[n]*switches[n] }
        dist=7.times.map { |m| 7.times.sum(Rational(0)) { |n| dist[n]*p[n][m] } }
        raise 'mass leaked' unless dist.sum==1
      end
      {congestion:congestion,gross_switches:moves,
       social_cost:congestion+fee*moves,final_occupancy:dist.freeze}
    end
  end
end
