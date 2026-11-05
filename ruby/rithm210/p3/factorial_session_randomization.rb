# frozen_string_literal: true
# RITHM P3-R17C: randomized 2x2 cluster design; group/session is the
# randomization unit. Within-cluster spillovers allowed, between-cluster
# interference excluded BY ASSUMPTION. No human trial conducted.
module Rithm210FactorialSessionRandomization
  module_function
  ARMS=[:sim_frozen,:sim_refreshed,:seq_frozen,:seq_refreshed].freeze
  def assignment(session_ids,seed:20261105)
    raise ArgumentError,'unique sessions divisible by four required' unless
      session_ids.uniq.size==session_ids.size && session_ids.size.positive? && session_ids.size%4==0
    shuffled=session_ids.shuffle(random:Random.new(seed))
    shuffled.each_with_index.to_h{|id,i|[id,ARMS[i%4]]}
  end
  def effects(assignment,outcome)
    raise ArgumentError,'outcome keys must equal assignment keys' unless assignment.keys.sort==outcome.keys.sort
    cells=ARMS.to_h{|arm|[arm,[]]}
    assignment.each do |id,arm|
      raise ArgumentError,'invalid arm/outcome' unless cells.key?(arm) && outcome.fetch(id).is_a?(Numeric)
      cells[arm]<<outcome.fetch(id).to_f
    end
    raise ArgumentError,'missing or unbalanced arm' unless cells.values.map(&:size).uniq==[cells.values.first.size] && cells.values.first.size>0
    m=cells.transform_values{|values|values.sum/values.size}
    {arm_means:m,
     schedule_when_frozen:m[:seq_frozen]-m[:sim_frozen],
     refresh_under_simultaneous:m[:sim_refreshed]-m[:sim_frozen],
     refresh_under_sequential:m[:seq_refreshed]-m[:seq_frozen],
     interaction:(m[:seq_refreshed]-m[:seq_frozen])-(m[:sim_refreshed]-m[:sim_frozen])}
  end
  def finite_population_interaction(potential_outcomes)
    raise ArgumentError,'empty population' if potential_outcomes.empty?
    potential_outcomes.values.each do |v|
      raise ArgumentError,'incomplete outcomes' unless ARMS.all?{|a|v[a].is_a?(Numeric)}
    end
    potential_outcomes.values.sum{|x|(x[:seq_refreshed]-x[:seq_frozen])-
      (x[:sim_refreshed]-x[:sim_frozen])}/potential_outcomes.size.to_f
  end
end
