# frozen_string_literal: true
require_relative 'r66_t14_decision'
require_relative 'r66_t13_kernel'
module RithmT14
  module Kernel
    module_function
    def transition(schedule:,mechanism:,policy: :baseline,disclosure:1)
      w=RithmT12::Schedules.validate(schedule)
      7.times.map do |n|
        a=Decision.flip_probability(n,:a,mechanism:mechanism,policy:policy,disclosure:disclosure)
        b=Decision.flip_probability(n,:b,mechanism:mechanism,policy:policy,disclosure:disclosure)
        row=Array.new(7,Rational(0))
        w.each_with_index do |p,mask|
          next if p.zero?
          aa=(0...n).count { |i| (mask & (1<<i))!=0 }
          bb=(n...6).count { |i| (mask & (1<<i))!=0 }
          q=RithmT13::Kernel.single_row(n,aa,bb,a,b)
          7.times { |m| row[m]+=p*q[m] }
        end
        raise 'mass leak' unless row.sum==1 && row.all? { |p| p>=0 }
        row.freeze
      end.freeze
    end
    def forecast(n0:,horizon:,schedule:,mechanism:,policy: :baseline,disclosure:1)
      raise ArgumentError, 'initial state/horizon' unless (0..6).cover?(n0) && n0.is_a?(Integer) && horizon.is_a?(Integer) && horizon.positive?
      p=transition(schedule:schedule,mechanism:mechanism,policy:policy,disclosure:disclosure)
      d=Array.new(7,Rational(0));d[n0]=1
      cost=Rational(0)
      horizon.times do |t|
        cost+=7.times.sum(Rational(0)) { |n| d[n]*3*(n-4)**2 }
        next if t==horizon-1
        d=7.times.map { |m| 7.times.sum(Rational(0)) { |n| d[n]*p[n][m] } }
      end
      {congestion:cost, final:d.freeze}
    end
  end
end
