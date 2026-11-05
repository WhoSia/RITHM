# frozen_string_literal: true
# R18-P3: synthetic protocol event-log verifier for a truthful sequential 2x2.
# A specification/acceptance test, NOT an implementation recruiting people.
require_relative 'lagged_feedback_factorial'
module Rithm210R18TruthfulSignalAudit
  module_function
  BASE=Rithm210UpdateClockSignalFactorial
  def check_round(previous_mask:,initial_mask:,report_age:,feedback:,events:)
    BASE.occupancy(previous_mask);BASE.occupancy(initial_mask)
    raise ArgumentError,'report age' unless %i[lagged current].include?(report_age)
    raise ArgumentError,'feedback must be boolean' unless [true,false].include?(feedback)
    raise ArgumentError,'exactly six microactions required' unless events.is_a?(Array) && events.size==6
    previous_n=BASE.occupancy(previous_mask)
    starting_n=BASE.occupancy(initial_mask)
    initial_report=report_age==:lagged ? previous_n : starting_n
    initial_stamp=report_age==:lagged ? :previous_period : :current_period
    state=initial_mask
    seen={}
    events.each_with_index do |e,index|
      raise ArgumentError,'event record' unless e.is_a?(Hash)
      actor=e.fetch(:actor)
      before=e.fetch(:before_mask)
      after=e.fetch(:after_mask)
      shown=e.fetch(:shown_n)
      stamp=e.fetch(:report_stamp)
      raise ArgumentError,'actor out of range or duplicated' unless actor.is_a?(Integer) && actor.between?(0,5) && !seen[actor]
      raise ArgumentError,'out of order state' unless before==state
      expected_n=feedback && index>0 ? BASE.occupancy(state) : initial_report
      expected_stamp=feedback && index>0 ? :current_period : initial_stamp
      raise ArgumentError,'untrue, stale or incorrectly timestamped signal' unless shown==expected_n && stamp==expected_stamp
      raise ArgumentError,'illegal simultaneous action or invalid state' unless
        after.is_a?(Integer) && after.between?(0,63) && (after^state).then{|bits|bits==0 || bits==(1<<actor)}
      seen[actor]=true
      state=after
    end
    raise 'not all actors served' unless seen.size==6
    {final_mask:state,final_occupancy:BASE.occupancy(state),
     opportunities:seen.size,trace_valid:true}
  end
  def example(previous_mask:3,initial_mask:15,report_age: :lagged,feedback:true)
    BASE.occupancy(previous_mask);BASE.occupancy(initial_mask)
    current=initial_mask
    original=report_age==:lagged ? BASE.occupancy(previous_mask) : BASE.occupancy(initial_mask)
    original_stamp=report_age==:lagged ? :previous_period : :current_period
    actions=[0,5,1,4,2,3].each_with_index.map do |actor,index|
      report_n=feedback && index>0 ? BASE.occupancy(current) : original
      stamp=feedback && index>0 ? :current_period : original_stamp
      following= index.even? ? current^(1<<actor) : current
      item={actor:actor,before_mask:current,after_mask:following,shown_n:report_n,report_stamp:stamp}
      current=following
      item
    end
    {previous_mask:previous_mask,initial_mask:initial_mask,
     report_age:report_age,feedback:feedback,events:actions}
  end
end
