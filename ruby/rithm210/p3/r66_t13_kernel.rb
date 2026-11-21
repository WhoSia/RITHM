# frozen_string_literal: true
require_relative 'r66_t13_mechanisms'
module RithmT13
  module Kernel
    module_function
    def single_row(n,activated_a,activated_b,pa,pb)
      out=Array.new(7,Rational(0))
      (0..activated_a).each do |d|
        pd=Rational(RithmT12::Schedules.choose(activated_a,d))*pa**d*(1-pa)**(activated_a-d)
        (0..activated_b).each do |u|
          pu=Rational(RithmT12::Schedules.choose(activated_b,u))*pb**u*(1-pb)**(activated_b-u)
          out[n-d+u]+=pd*pu
        end
      end
      raise 'mass leak' unless out.sum==1
      out
    end
    def transitions(schedule:,threshold:0,attention:1,respond:Rational(2,5),lapse:Rational(1,50),bias_a:0,bias_b:0)
      sched=RithmT12::Schedules.validate(schedule)
      rows=[];gross=[]
      7.times do |n|
        pa,pb=Mechanisms.route_rates(n,threshold:threshold,attention:attention,respond:respond,lapse:lapse,bias_a:bias_a,bias_b:bias_b)
        out=Array.new(7,Rational(0));changes=Rational(0)
        sched.each_with_index do |w,mask|
          next if w.zero?
          aa=(0...n).count { |i| (mask&(1<<i))!=0 }
          bb=(n...6).count { |i| (mask&(1<<i))!=0 }
          row=single_row(n,aa,bb,pa,pb)
          out.each_index { |k| out[k]+=w*row[k] }
          changes+=w*(aa*pa+bb*pb)
        end
        raise 'transition mass leak' unless out.sum==1
        rows << out.freeze;gross << changes
      end
      [rows.freeze,gross.freeze]
    end
    def total(n0:,horizon:40,schedule:,real_resource_fee:0,**params)
      raise ArgumentError,'n0/horizon' unless n0.is_a?(Integer) && n0.between?(0,6) && horizon.is_a?(Integer) && horizon.positive?
      fee=Rational(real_resource_fee)
      raise ArgumentError,'real fee' if fee.negative?
      trans,gross=transitions(schedule:schedule,**params)
      d=Array.new(7,Rational(0));d[n0]=1
      congestion=Rational(0);revisions=Rational(0)
      horizon.times do |t|
        congestion+=7.times.sum(Rational(0)) { |n| d[n]*3*(n-4)**2 }
        next if t==horizon-1
        revisions+=7.times.sum(Rational(0)) { |n| d[n]*gross[n] }
        d=7.times.map { |k| 7.times.sum(Rational(0)) { |n| d[n]*trans[n][k] } }
      end
      {congestion:congestion,gross_switches:revisions,social_cost:congestion+fee*revisions,final:d.freeze}
    end
  end
end
