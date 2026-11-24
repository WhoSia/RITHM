# frozen_string_literal: true
require_relative 'r66_t14_kernel'
module RithmT14
  module Accounting
    module_function
    # Physical fees are extra resource losses, not the private perceived thresholds.
    # Per-offer resource fee is for exogenous disclosure even if recipient does not switch.
    def forecast(n0:,horizon:,schedule:,mechanism:,policy: :baseline,disclosure:1,switch_fee:0,offer_fee:0)
      raise ArgumentError,'initial state/horizon' unless n0.is_a?(Integer) && n0.between?(0,6) && horizon.is_a?(Integer) && horizon.positive?
      sf,of=Rational(switch_fee),Rational(offer_fee)
      raise ArgumentError,'negative resource fee' if sf.negative? || of.negative?
      s=RithmT12::Schedules
      weights=s.validate(schedule)
      marginals=6.times.map { |i| s.marginal(weights,i) }
      raise ArgumentError,'unequal eligibility marginals' unless marginals.uniq.length==1
      theta=marginals.first
      p=Kernel.transition(schedule:weights,mechanism:mechanism,policy:policy,disclosure:disclosure)
      gross=7.times.map do |n|
        a=Decision.flip_probability(n,:a,mechanism:mechanism,policy:policy,disclosure:disclosure)
        b=Decision.flip_probability(n,:b,mechanism:mechanism,policy:policy,disclosure:disclosure)
        theta*(n*a+(6-n)*b)
      end
      d=Array.new(7,Rational(0));d[n0]=1
      congestion=Rational(0);switches=Rational(0)
      horizon.times do |t|
        congestion+=7.times.sum(Rational(0)) { |n| d[n]*3*(n-4)**2 }
        next if t==horizon-1
        switches+=7.times.sum(Rational(0)) { |n| d[n]*gross[n] }
        d=7.times.map { |m| 7.times.sum(Rational(0)) { |n| d[n]*p[n][m] } }
      end
      offers=policy==:free_info ? (horizon-1)*6*theta*Rational(disclosure) : 0
      {congestion:congestion,switches:switches,offers:offers,resource_total:congestion+sf*switches+of*offers}
    end
  end
end
