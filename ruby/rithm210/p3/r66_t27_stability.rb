# frozen_string_literal: true
require_relative 'r66_t27_compare'
module RithmT27
  module Stability
    C=Compare;F=Features
    module_function
    # Refit each leave-one-session-out analysis after deleting an entire other session.
    # Descriptive sensitivity, not a confidence interval for independent replications.
    def deletion(records,strength:12)
      groups=records.group_by(&:first);raise 'need three sessions' unless groups.size>=3
      values=groups.keys.map do |sid|
        C.evaluate(groups.reject{|k,_|k==sid}.values.flatten(1),strength:strength)[:contrasts].transform_values{|v|v[:mean]}
      end
      values.first.keys.to_h{|key|[key,{range:values.map{|v|v[key]}.minmax,negative:values.count{|v|v[key]<0},refits:values.size}]}
    end
    def audit(path)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      records=F.records(rows)
      sensitivity=[0.2,0.5,0.8].flat_map do |rho|
        rs=rho==0.5 ? records : F.records(rows,rho:rho)
        [3,12,48].map do |strength|
          x=C.evaluate(rs,strength:strength)
          {rho:rho,strength:strength,logloss:x[:scores].transform_values{|v|v[:session_logloss]}}
        end
      end
      {refit_deletion:deletion(records),parameter_sensitivity:sensitivity,source_sha256:s::SHA,aggregate_only:true}
    end
  end
end
puts JSON.pretty_generate(RithmT27::Stability.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
