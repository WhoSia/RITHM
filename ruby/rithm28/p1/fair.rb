require_relative '../p0r10/checker'
# Four-state restricted example: pending/ordered loops are unfair if their
# continuously enabled authorized/delivery escape remains postponed forever.
module P1Fair
 def self.starvation_lassos
  {pending:[:other],ordered:[:delay]}
 end
 def self.fair_starvation_lassos
  starvation_lassos.reject{|state,_|[:pending,:ordered].include?(state)}
 end
end
if __FILE__==$PROGRAM_NAME
raise unless P1Fair.starvation_lassos.size==2
raise unless P1Fair.fair_starvation_lassos.empty?
puts 'PASS: both non-restored lassos excluded under declared action-weak fairness'
end
