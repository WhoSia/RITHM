# frozen_string_literal: true
require_relative 'r66_t30_payoff'
module RithmT30
  module Sensitivity
    P=Payoff
    module_function
    # Paired whole-session contrast; no session IDs or per-session losses exported.
    def contrast(base,alt)
      raise ArgumentError,'fold mismatch' unless base.keys.sort==alt.keys.sort && !base.empty?
      ds=base.map do |sid,b|
        a=alt.fetch(sid);raise 'target mismatch' unless a[0]==b[0]
        a[1]-b[1]
      end
      info=[0,1].to_h do |i|
        diffs=base.filter_map do |sid,b|
          x=b[3][i];y=alt.fetch(sid)[3][i]
          raise 'stratum target mismatch' unless x[0]==y[0]
          (y[1]-x[1])/x[0] if x[0]>0
        end
        [i,{sessions:diffs.size,mean:diffs.empty? ? nil : diffs.sum/diffs.size,better:diffs.count(&:negative?)}]
      end
      {mean:ds.sum/ds.size,better:ds.count(&:negative?),sessions:ds.size,by_information:info}
    end
    def audit(path)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      paths=P.trajectories(rows)
      results=[12,40,80].map do |n|
        b=P.score_folds(paths,iterations:n);a=P.score_folds(paths,beta:0.15,iterations:n)
        {iterations:n,baseline:b.values.sum{|v|v[1]}/b.size,alternative:a.values.sum{|v|v[1]}/a.size,contrast:contrast(b,a)}
      end
      {results:results,source_sha256:s::SHA,aggregate_only:true}
    end
  end
end
puts JSON.pretty_generate(RithmT30::Sensitivity.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
