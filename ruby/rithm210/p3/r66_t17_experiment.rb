# frozen_string_literal: true
require_relative 'r66_t17_loop'
require 'json'
module RithmT17
  module Experiment
    module_function
    def mean_se(xs)
      m=xs.sum.to_f/xs.size; v=xs.sum { |x| (x-m)**2 }/(xs.size-1)
      {mean:m,se:Math.sqrt(v/xs.size)}
    end
    def compare(n:5,horizon:40,reps:600,rho:0.8,response:0.4,threshold:0,clock: :common,memory: :filter)
      raise ArgumentError,'replications' unless reps.is_a?(Integer) && reps>=2
      q=[0.0,0.5,1.0]; rows=q.to_h { |x| [x,[]] }
      reps.times do |i|
        tape=Loop.tape(170_000+i,horizon)
        q.each { |x| rows[x]<<Loop.run(n:n,tape:tape,clock:clock,rho:rho,disclosure:x,response:response,threshold:threshold,memory:memory) }
      end
      rows.map do |x,rs|
        v=rs.map { |r| r[:cost] };delta=v.zip(rows[0.0]).map { |cost,b| cost-b[:cost] }
        {disclosure:x,cost:mean_se(v),delta:mean_se(delta),switches:mean_se(rs.map { |r| r[:switches] }),terminal_optimum:rs.count { |r| r[:final]==4 }.to_f/reps}
      end
    end
    def grid(reps:600)
      [0.2,0.5,0.8].flat_map do |rho|
        Loop::CLOCKS.flat_map do |clock|
          [0.4,1.0].map do |response|
            {rho:rho,clock:clock,response:response,reps:reps,n:5,horizon:40,results:compare(reps:reps,rho:rho,clock:clock,response:response)}
          end
        end
      end
    end
  end
end
puts JSON.pretty_generate(RithmT17::Experiment.grid(reps:Integer(ARGV.fetch(0,'600')))) if $PROGRAM_NAME==__FILE__
