# frozen_string_literal: true
require 'json'
require_relative 'r66_t12_pairwise_identity'
module RithmT12
  module CLI
    module_function
    def run(horizon:40,fee:0)
      schedules={common:Schedules.common,independent:Schedules.independent,
                 staggered_three:Schedules.fixed_count(3)}
      cells={}
      [4,5].each do |n|
        cells[n.to_s]={}
        schedules.each do |label,w|
          out=Kernel.forecast(n0:n,horizon:horizon,schedule:w,fee:fee)
          cells[n.to_s][label]={
            congestion:out[:congestion].to_f.round(9),
            expected_switches:out[:gross_switches].to_f.round(9),
            welfare_with_fee:out[:social_cost].to_f.round(9),
            final_optimal_mass:out[:final_occupancy][4].to_f.round(9)
          }
        end
      end
      {study:'R66-T12 exact toy revision opportunities',language:'Ruby',
       fitted_human_behavior:false,horizon:horizon,physical_fee:fee,
       per_actor_opportunity:'1/2',
       pair_activation_covariance:{common:'1/4',independent:'0',staggered_three:'-1/20'},
       initial_four_common_minus_independent_one_step:
         PairwiseIdentity.expected_gap(4,schedules[:common],schedules[:independent]).to_s,
       results:cells}
    end
  end
end
puts JSON.pretty_generate(RithmT12::CLI.run) if $PROGRAM_NAME == __FILE__
