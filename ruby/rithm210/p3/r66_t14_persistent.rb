# frozen_string_literal: true
require_relative 'r66_t14_kernel'
module RithmT14
  module Persistent
    module_function
    S=RithmT12::Schedules
    # High-cost types remain in their initial routes; low-cost types revise
    # when their current unilateral gain is strictly positive and eligible.
    # Types are independent fair draws at t=0, then frozen. No learning/update.
    def type_law(n0)
      raise ArgumentError,'occupancy' unless n0.is_a?(Integer) && n0.between?(0,6)
      (0..n0).flat_map do |ha|
        (0..(6-n0)).map do |hb|
          [ha,hb,Rational(S.choose(n0,ha)*S.choose(6-n0,hb),64)]
        end
      end
    end
    def transition(ha,hb,schedule)
      raise ArgumentError,'invalid type counts' unless [ha,hb].all? { |x| x.is_a?(Integer) && x>=0 } && ha+hb<=6
      w=S.validate(schedule); m=6-ha-hb
      (0..m).map do |j|
        n=ha+j;row=Array.new(m+1,Rational(0))
        a=Decision.gain(n,:a)>0;b=Decision.gain(n,:b)>0
        w.each_with_index do |p,mask|
          next if p.zero?
          d=a ? (0...j).count { |i| (mask&(1<<i))!=0 } : 0
          u=b ? (j...m).count { |i| (mask&(1<<i))!=0 } : 0
          row[j-d+u]+=p
        end
        raise 'mass leak' unless row.sum==1
        row.freeze
      end.freeze
    end
    def forecast(n0:,horizon:,schedule:)
      raise ArgumentError,'horizon' unless horizon.is_a?(Integer) && horizon.positive?
      total=Rational(0);out=Array.new(7,Rational(0))
      type_law(n0).each do |ha,hb,weight|
        p=transition(ha,hb,schedule);m=6-ha-hb
        d=Array.new(m+1,Rational(0));d[n0-ha]=1
        horizon.times do |t|
          total+=weight*(0..m).sum(Rational(0)) { |j| d[j]*3*(ha+j-4)**2 }
          next if t==horizon-1
          d=(0..m).map { |k| (0..m).sum(Rational(0)) { |j| d[j]*p[j][k] } }
        end
        d.each_with_index { |v,j| out[ha+j]+=weight*v }
      end
      raise 'mass leak' unless out.sum==1
      {congestion:total,final:out.freeze}
    end
  end
end
