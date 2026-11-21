# frozen_string_literal: true
# Explicitly distinguish perceived gain threshold from realized physical fee.
require_relative 'r66_t12_schedules'
module RithmT13
  module Mechanisms
    module_function
    def private_gain(n,route)
      raise ArgumentError,'occupancy' unless n.is_a?(Integer) && n.between?(0,6)
      case route
      when :a then 3*n-14
      when :b then 11-3*n
      else raise ArgumentError,'route'
      end
    end
    def rate(gain:,threshold:0,attention:1,respond:Rational(2,5),lapse:Rational(1,50),bias:0)
      attention=Rational(attention);respond=Rational(respond);lapse=Rational(lapse)
      raise ArgumentError,'probability bounds' unless [attention,respond,lapse].all? { |x| x.between?(0,1) }
      raise ArgumentError,'nonnegative private threshold' unless Rational(threshold)>=0
      # Not a fully structural reference-dependent preference model.
      reacts=Rational(gain)+Rational(bias)>Rational(threshold)
      attention*(reacts ? respond : lapse)+(1-attention)*lapse
    end
    def route_rates(n,threshold:0,attention:1,respond:Rational(2,5),lapse:Rational(1,50),bias_a:0,bias_b:0)
      [rate(gain:private_gain(n,:a),threshold:threshold,attention:attention,respond:respond,lapse:lapse,bias:bias_a),
       rate(gain:private_gain(n,:b),threshold:threshold,attention:attention,respond:respond,lapse:lapse,bias:bias_b)]
    end
  end
end
