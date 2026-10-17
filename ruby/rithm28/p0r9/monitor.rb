# frozen_string_literal: true
# RITHM 2.8 P0-R9. Constructed finite rights-event monitor; no real cases.
module RithmR9
 def self.authority_trace(events,authorized_body: :authorized)
  state=:initial; history=[]
  events.each do |event|
   case event.fetch(:event)
   when :drop then state=:dropped
   when :appeal_file then state=:appeal_pending if state==:dropped
   when :repair_decision
    state=:repair_ordered if state==:appeal_pending && event[:body]==authorized_body
   when :deliver
    state=:restored if state==:repair_ordered && event[:receipt]==true
   else raise ArgumentError,'unknown event'
   end
   history << state
  end
  {final:state,history:history,restored:history.include?(:restored)}
 end
 def self.quotient_counterexample
  a={pending:['B2'],served:['A1'],dropped:['B2:first'],appeal_eligible:['B2']}
  b={pending:['A2'],served:['A1'],dropped:['B2:first'],appeal_eligible:['B2']}
  projection=->(x){[x[:pending].length,x[:served].length,x[:dropped].length,x[:appeal_eligible].length]}
  raise 'not same aggregate' unless projection.call(a)==projection.call(b)
  {aggregate:projection.call(a),pending_b2_a:a[:pending].include?('B2'),pending_b2_b:b[:pending].include?('B2')}
 end
end
