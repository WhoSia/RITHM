require_relative 'r66_t18_learning'
require 'json'
module RithmT18
  module Experiment
    module_function
    def summary(xs)
      m=xs.sum.to_f/xs.size
      {mean:m,se:Math.sqrt(xs.sum { |x| (x-m)**2 }/(xs.size-1)/xs.size)}
    end
    def grid(reps:100,horizon:40,seed:190_000)
      raise ArgumentError,'reps/horizon' unless reps>=2 && horizon>=3
      modes={fixed:[[0.5],0],learn:[[0.2,0.8],0],forget:[[0.2,0.8],0.25]}
      CLOCKS.product([0.4,1.0],[0.0,0.5,1.0]).map do |clock,response,q|
        rows=modes.keys.to_h { |m| [m,[]] }
        reps.times do |i|
          t=RithmT18.tape(seed+i,horizon)
          modes.each do |m,(g,f)|
            rows[m]<<RithmT18.run(n:5,tape:t,clock:clock,grid:g,disclosure:q,response:response,forget:f)
          end
        end
        base=rows[:fixed].map { |r| r[:cost] }
        {clock:clock,response:response,disclosure:q,reps:reps,horizon:horizon,seed:seed,results:rows.transform_values do |rs|
          {cost:summary(rs.map { |r| r[:cost] }),delta:summary(rs.map { |r| r[:cost] }.zip(base).map { |a,b| a-b }),logloss:summary(rs.map { |r| r[:logloss] }),rho:summary(rs.map { |r| r[:rho] }),exit_rate:rs.count { |r| r[:first_exit] }.to_f/reps}
        end}
      end
    end
  end
end
puts JSON.pretty_generate(RithmT18::Experiment.grid(reps:Integer(ARGV.fetch(0,'100')))) if $PROGRAM_NAME==__FILE__
