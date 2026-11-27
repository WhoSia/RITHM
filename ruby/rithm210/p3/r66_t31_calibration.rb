# frozen_string_literal: true
require_relative 'r66_t30_group'
require_relative 'r66_t31_coupling'
module RithmT31
  module Calibration
    G=RithmT30::Group; C=Coupling
    WEIGHTS=[-0.25,-0.10,0.0,0.10,0.25].freeze
    module_function
    def metrics(ps,actual)
      nominal=G.metrics(ps,actual);q=G.occupancy(ps);n=actual.sum
      lo,hi=C.bounds(ps)
      residual=actual.zip(ps).map{|a,p|a-p}
      linear=3*residual.each_with_index.sum{|e,i|(2*ps.sum-7-2*ps[i])*e}
      pair=90*nominal[:pair_residual]
      lower=C.occupancy(C.lower(ps),6);upper=C.occupancy(C.upper(ps),6)
      losses=WEIGHTS.map do |w|
        alternative=w<0 ? lower : upper
        -Math.log((1-w.abs)*q[n]+w.abs*alternative[n].to_f)
      end
      {lower:lo.to_f,upper:hi.to_f,actual:nominal[:actual_cost],independent:nominal[:predicted_cost],linear_residual:linear,pair_residual:pair,identity_error:(nominal[:actual_cost]-nominal[:predicted_cost]-linear-pair).abs,losses:losses}
    end
    def evaluate(paths,beta:0.15,iterations:40)
      folds=[]
      baseline=G.evaluate(paths,beta:beta,iterations:iterations) do |groups|
        rows=groups.map{|ps,a|metrics(ps,a)}
        means=rows.first.keys.reject{|k|[:identity_error,:losses].include?(k)}.to_h{|k|[k,rows.sum{|r|r[k]}.fdiv(rows.size)]}
        folds<<means.merge(identity_error:rows.map{|r|r[:identity_error]}.max,losses:WEIGHTS.each_index.map{|i|rows.sum{|r|r[:losses][i]}.fdiv(rows.size)})
      end
      {baseline:baseline,costs:folds.first.keys.reject{|k|[:identity_error,:losses].include?(k)}.to_h{|k|[k,folds.sum{|r|r[k]}.fdiv(folds.size)]},max_identity_error:folds.map{|r|r[:identity_error]}.max,mixtures:WEIGHTS.each_with_index.map{|w,i|{weight:w,session_logloss:folds.sum{|r|r[:losses][i]}.fdiv(folds.size),better:folds.count{|r|r[:losses][i]<r[:losses][2]}}}}
    end
    def audit(path)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      evaluate(G::P.trajectories(rows)).merge(source_sha256:s::SHA,aggregate_only:true)
    end
  end
end
puts JSON.pretty_generate(RithmT31::Calibration.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
