# frozen_string_literal: true
require_relative 'r66_t26_source_contract'
module RithmT26
  module Forecast
    MODES=[:route,:observation,:history,:both].freeze
    module_function
    def keys(row,previous)
      a=Integer(row['RouteA']);info=Integer(row['Informed'])
      raise 'route/info' unless [0,1].include?(a) && [0,1].include?(info)
      base=[row['trt'],info,a];past=(a-Integer(previous['RouteA'])).abs
      if info==1
        obs=Integer(row['NumA'])-a
        raise 'occupancy' unless obs.between?(0,5)
      else
        y=Rational(row['profit']);obs=(0..5).sum{|k|(6..16).cover?(y+(a==1 ? k+1 : 2*(6-k))) ? 1<<k : 0}
        raise 'payoff incompatible' if obs==0
      end
      [base,base+[obs],base+[past],base+[obs,past]]
    end
    def records(rows,periods:40)
      index=rows.to_h{|r|[r.values_at('session','Group','trt','ID')+[Integer(r['Period'])],r]}
      raise 'duplicate row' unless index.size==rows.size
      rows.filter_map do |r|
        t=Integer(r['Period']);next unless t.between?(2,periods-1)
        k=r.values_at('session','Group','trt','ID');previous=index.fetch(k+[t-1]);future=index.fetch(k+[t+1])
        [r['session'],keys(r,previous),(Integer(r['RouteA'])-Integer(future['RouteA'])).abs]
      end
    end
    def tables
      Array.new(4){Hash.new{|h,k|h[k]=[0,0]}}
    end
    def fit(records)
      all=tables;held=Hash.new{|h,k|h[k]=tables}
      records.each do |sid,ks,y|
        raise 'binary target' unless [0,1].include?(y)
        ks.each_with_index do |k,i|
          [all[i][k],held[sid][i][k]].each{|v|v[0]+=1;v[1]+=y}
        end
      end
      [all,held]
    end
    # Training counts exclude all rows from the held session. Fixed shrinkage, no tuning.
    def predict(ks,all,held,strength:12)
      raise ArgumentError,'strength' unless strength>0
      n,y=all[0][ks[0]].zip(held[0][ks[0]]).map{|a,b|a-b};p0=(y+1.0)/(n+2)
      out=[p0]
      [1,2,3].each do |i|
        n,y=all[i][ks[i]].zip(held[i][ks[i]]).map{|a,b|a-b}
        prior=i==3 ? out[1] : p0;out<<(y+strength*prior)/(n+strength)
      end
      out
    end
    def evaluate(records,strength:12)
      all,held=fit(records);raise 'need at least two sessions' unless held.size>=2
      folds=held.keys.to_h{|sid|[sid,Array.new(4){[0,0.0,0.0]}]}
      records.each do |sid,ks,y|
        predict(ks,all,held.fetch(sid),strength:strength).each_with_index do |p,i|
          v=folds.fetch(sid)[i];v[0]+=1;v[1]-=Math.log(y==1 ? p : 1-p);v[2]+=(p-y)**2
        end
      end
      scores=MODES.each_with_index.to_h do |mode,i|
        vs=folds.values.map{|v|v[i]};n=vs.sum(&:first)
        [mode,{n:n,pooled_logloss:vs.sum{|v|v[1]}/n,session_mean_logloss:vs.sum{|v|v[1]/v[0]}/vs.size,session_mean_brier:vs.sum{|v|v[2]/v[0]}/vs.size}]
      end
      diffs=folds.values.map{|v|(v[3][1]-v[1][1])/v[1][0]}
      {sessions:held.size,records:records.size,strength:strength,scores:scores,both_minus_observation_sessions_better:diffs.count(&:negative?),both_minus_observation_session_mean:diffs.sum/diffs.size}
    end
    def audit(path)
      rows=SourceContract.read_rows(path);check=SourceContract.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      evaluate(records(rows)).merge(source_sha256:SourceContract::SHA,aggregate_only:true)
    end
  end
end
puts JSON.pretty_generate(RithmT26::Forecast.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
