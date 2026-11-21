# frozen_string_literal: true
require_relative 'r66_t13_counterexamples'
module RithmT13
  module AttentionInteraction
    module_function
    def contrast(low:Rational(1,2),high:1,threshold:0,n0:4,horizon:40)
      raise ArgumentError,'attention comparison' unless Rational(high)>Rational(low) && Rational(high)<=1 && Rational(low)>=0
      a=Counterexamples.cell(attention:low,threshold:threshold,n0:n0,horizon:horizon)
      b=Counterexamples.cell(attention:high,threshold:threshold,n0:n0,horizon:horizon)
      effects=a.keys.to_h { |s| [s,b[s][:congestion]-a[s][:congestion]] }
      {effect_by_clock:effects,
       interaction_shared_minus_independent:effects[:common]-effects[:independent],
       interaction_staggered_minus_independent:effects[:fixed_three]-effects[:independent]}
    end
  end
end
