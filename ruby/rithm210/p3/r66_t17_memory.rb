# frozen_string_literal: true
require_relative 'r66_t17_experiment'
module RithmT17
  module MemoryComparison
    module_function
    def run(reps:400)
      raise ArgumentError,'replications' unless reps.is_a?(Integer) && reps>=2
      Loop::CLOCKS.flat_map do |clock|
        [0.0,0.5,1.0].map do |q|
          a=[];b=[]
          reps.times do |i|
            tape=Loop.tape(180000+i,40)
            x={n:5,tape:tape,clock:clock,rho:0.8,disclosure:q,response:0.4}
            a<<Loop.run(**x,memory: :filter)[:cost]
            b<<Loop.run(**x,memory: :reset)[:cost]
          end
          {clock:clock,disclosure:q,filter:Experiment.mean_se(a),reset:Experiment.mean_se(b),delta:Experiment.mean_se(a.zip(b).map { |x,y| x-y })}
        end
      end
    end
  end
end
puts JSON.pretty_generate(RithmT17::MemoryComparison.run(reps:Integer(ARGV.fetch(0,'400')))) if $PROGRAM_NAME==__FILE__
