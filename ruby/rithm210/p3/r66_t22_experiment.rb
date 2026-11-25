require_relative 'r66_t22_context'
require 'json'
module RithmT22
  module Experiment
    C=Context
    module_function
    def stat(x)
      m=x.sum.to_f/x.size;{mean:m,se:Math.sqrt(x.sum{|v|(v-m)**2}/(x.size-1)/x.size)}
    end
    def grid(reps:160,seed:220_000,horizon:40)
      C::CLOCKS.product([0.4,1.0]).map do |clock,response|
        costs=C::MODES.to_h{|m|[m,[]]};scores=C::MODES.to_h{|m|[m,C::MODES.to_h{|p|[p,[0.0,0]]}]}
        reps.times do |i|
          t=C.tape(seed+i,horizon)
          C::MODES.each do |m|
            r=C.run(tape:t,clock:clock,response:response,mode:m);costs[m]<<r[:cost]
            C.replay(r[:paths]).each do |p,(s,n)|
              scores[m][p][0]+=s;scores[m][p][1]+=n
            end
          end
        end
        {clock:clock,response:response,reps:reps,seed:seed,horizon:horizon,cost:costs.transform_values{|v|stat(v)},conditional_minus_pooled:stat(costs[:conditional].zip(costs[:pooled]).map{|a,b|a-b}),scores:scores.transform_values{|h|h.transform_values{|s,n|{logloss:s/n,count:n}}}}
      end
    end
  end
end
puts JSON.pretty_generate(RithmT22::Experiment.grid(reps:Integer(ARGV.fetch(0,'160')))) if $PROGRAM_NAME==__FILE__
