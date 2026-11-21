# frozen_string_literal: true
require_relative 'r66_t13_kernel'
require 'json'
module RithmT13
  module Counterexamples
    module_function
    def cell(n0:4,horizon:40,threshold:0,attention:1,fee:0)
      s=RithmT12::Schedules
      laws={common:s.common,independent:s.independent,fixed_three:s.fixed_count(3)}
      laws.transform_values do |w|
        Kernel.total(n0:n0,horizon:horizon,schedule:w,threshold:threshold,
                     attention:attention,real_resource_fee:fee)
      end
    end
    def order(result)
      result.keys.sort_by { |k| result[k][:social_cost] }
    end
    def public_summary
      inputs=[{attention:1,threshold:0},
              {attention:Rational(1,2),threshold:0},
              {attention:Rational(1,2),threshold:2},
              {attention:0,threshold:0},
              {attention:1,threshold:5}]
      {model:'hypothetical symmetric six-actor cost/rule',
       original_subject_data_included:false,
       cells:inputs.map do |params|
         x=cell(**params)
         {attention:params[:attention].to_s,threshold:params[:threshold],
          rank:order(x),
          cost:x.transform_values { |v| v[:congestion].to_f.round(8) },
          gross:x.transform_values { |v| v[:gross_switches].to_f.round(8) }}
       end}
    end
  end
end
puts JSON.pretty_generate(RithmT13::Counterexamples.public_summary) if $PROGRAM_NAME == __FILE__
