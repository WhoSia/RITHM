# frozen_string_literal: true
# RITHM R17F: sequential-only 2x2 that independently randomizes truthful
# previous-period vs current-period initial occupancy and microstep feedback.
# All six actors act ONCE, in uniformly random order. No deceptive reports.
require_relative 'smooth_signal_clock'
module Rithm210LaggedFeedbackFactorial
  module_function
  S=Rithm210SmoothSignalClock
  B=Rithm210UpdateClockSignalFactorial
  def transition(mask,previous_n:,initial_report:,within_round_refresh:,strength:0.3,
                 tremble:0.1,biases:Array.new(6,0.0),shock:0.0)
    current_n=B.occupancy(mask)
    raise ArgumentError,'previous occupancy must be 0..6' unless previous_n.is_a?(Integer) && previous_n.between?(0,6)
    raise ArgumentError,'initial report age' unless %i[lagged current].include?(initial_report)
    raise ArgumentError,'boolean refresh required' unless [true,false].include?(within_round_refresh)
    S.validate!(strength:strength,tremble:tremble,biases:biases,shock:shock)
    initial=initial_report==:lagged ? previous_n : current_n
    states={[0,mask]=>1.0}
    6.times do |step|
      nxt=Hash.new(0.0)
      states.each do |(selected,current),mass|
        6.times do |actor|
          bit=1<<actor
          next unless (selected & bit)==0
          perceived=within_round_refresh && step>0 ? B.occupancy(current) : initial
          p=S.probability((current & bit)!=0,perceived,actor:actor,
            strength:strength,tremble:tremble,biases:biases,shock:shock)
          share=mass/(6-step)
          nxt[[selected|bit,current]]+=share*(1-p)
          nxt[[selected|bit,current^bit]]+=share*p
        end
      end
      states=nxt
    end
    out=Hash.new(0.0)
    states.each{|(selected,state),mass|raise 'actor missing' unless selected==63;out[state]+=mass}
    raise 'mass lost' unless (out.values.sum-1).abs<1e-10
    out
  end
  def factorial(mask:15,previous_n:2,**opts)
    outcomes={}
    %i[lagged current].each do |initial|
      [false,true].each do |feedback|
        states=transition(mask,previous_n:previous_n,initial_report:initial,
          within_round_refresh:feedback,**opts)
        hist=Array.new(7,0.0)
        states.each{|state,p|hist[B.occupancy(state)]+=p}
        outcomes[[initial,feedback]]={excess:S.expected_excess(hist),distribution:hist}
      end
    end
    e=->(i,r){outcomes.fetch([i,r])[:excess]}
    {outcomes:outcomes,initial_fresh_effect_without_feedback:e.call(:current,false)-e.call(:lagged,false),
     feedback_effect_lagged:e.call(:lagged,true)-e.call(:lagged,false),
     feedback_effect_current:e.call(:current,true)-e.call(:current,false),
     interaction:(e.call(:current,true)-e.call(:current,false))-
       (e.call(:lagged,true)-e.call(:lagged,false)),
     scope:'Within SEQUENTIAL CLOCK only; all reports truthfully stamped previous or current. No human experiment.'}
  end
end
