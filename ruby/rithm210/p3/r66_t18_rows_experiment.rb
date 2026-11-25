require_relative 'r66_t18_rows'
require_relative 'r66_t18_experiment'
require 'json'
module RithmT18
  module RowsExperiment
    module_function
    def grid(reps:100,horizon:40,seed:191_000)
      modes=[:fixed,:sticky,:rows,:rows_forget]
      CLOCKS.product([0.4,1.0]).map do |clock,response|
        costs=modes.to_h { |m| [m,[]] }; scores=modes.to_h { |m| [m,modes.to_h { |x| [x,[]] }] }
        reps.times do |i|
          t=RithmT18.tape(seed+i,horizon)
          modes.each do |m|
            r=Full.run(tape:t,clock:clock,response:response,mode:m); costs[m]<<r[:cost]
            Full.replay(r[:paths]).each { |pred,loss| scores[m][pred]<<loss }
          end
        end
        {clock:clock,response:response,reps:reps,horizon:horizon,seed:seed,costs:costs.transform_values { |v| Experiment.summary(v) },deltas:costs.transform_values { |v| Experiment.summary(v.zip(costs[:fixed]).map { |a,b| a-b }) },replay:scores.transform_values { |v| v.transform_values { |xs| Experiment.summary(xs) } }}
      end
    end
  end
end
puts JSON.pretty_generate(RithmT18::RowsExperiment.grid(reps:Integer(ARGV.fetch(0,'100')))) if $PROGRAM_NAME==__FILE__
