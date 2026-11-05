# frozen_string_literal: true
require_relative 'r18_truthful_signal_audit'
module Rithm210R18RoundChainAudit
  module_function
  Audit=Rithm210R18TruthfulSignalAudit
  PROTOCOLS={
    lagged_frozen:[:lagged,false],lagged_feedback:[:lagged,true],
    current_frozen:[:current,false],current_feedback:[:current,true]
  }.freeze
  HORIZON=40
  def cost(n)
    raise ArgumentError,'n must be an integer 0..6' unless n.is_a?(Integer)&&n.between?(0,6)
    n*n+2*(6-n)**2
  end
  def verify(protocol:,baseline_previous_mask:,baseline_current_mask:,baseline_timestamp:,assignment_timestamp:,rounds:)
    age,feedback=PROTOCOLS.fetch(protocol){raise ArgumentError,'unknown protocol'}
    Audit.occ(baseline_previous_mask);Audit.occ(baseline_current_mask)
    unless [baseline_timestamp,assignment_timestamp].all?{|v|v.is_a?(Numeric)&&v.finite?}&&baseline_timestamp<assignment_timestamp
      raise ArgumentError,'baseline must precede allocation'
    end
    raise ArgumentError,'exactly 40 rounds required' unless rounds.is_a?(Array)&&rounds.size==HORIZON
    prev=baseline_previous_mask;current=baseline_current_mask;total=0
    rounds.each_with_index do |r,t|
      raise ArgumentError,'period mismatch' unless r.is_a?(Hash)&&r[:period]==t+1
      raise ArgumentError,'history mismatch' unless r[:previous_mask]==prev&&r[:initial_mask]==current
      raise ArgumentError,'protocol changed' if r.key?(:protocol)&&r[:protocol]!=protocol
      check=Audit.check_round(previous_mask:prev,initial_mask:current,
        report_age:age,feedback:feedback,events:r.fetch(:events))
      total+=cost(Audit.occ(current))
      prev,current=current,check.fetch(:final_mask)
    end
    {protocol:protocol,complete:true,rounds:HORIZON,opportunities:HORIZON*6,
     cumulative_cost:total,cumulative_excess:total-24*HORIZON,
     terminal_occupancy:Audit.occ(current)}
  end
end
