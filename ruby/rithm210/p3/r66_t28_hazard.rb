# frozen_string_literal: true
require_relative 'r66_t26_forecast'
module RithmT28
  module Hazard
    F=RithmT26::Forecast
    MODES=[:route,:observation,:phase,:directional,:recent,:duration,:duration_origin].freeze
    PARENTS=[nil,0,1,2,3,3,5].freeze
    module_function
    def records(rows,periods:40)
      rows.group_by{|r|r.values_at('session','Group','trt','ID')}.flat_map do |id,rs|
        rs=rs.sort_by{|r|Integer(r['Period'])}
        raise 'incomplete trajectory' unless rs.map{|r|Integer(r['Period'])}==(1..periods).to_a
        exposures=[0,0];switches=[0,0];duration=0;changed=false;previous=nil
        rs.each_with_index.filter_map do |r,i|
          a=Integer(r['RouteA']);base,obs=F.keys(r,previous||r).take(2)
          past=0
          if previous
            old=Integer(previous['RouteA']);past=(a-old).abs
            exposures[old]+=1;switches[old]+=past
            changed ||= past==1
          end
          duration=past==1 ? 1 : duration+1;previous=r
          next if i==0 || i==periods-1
          phase=obs+[i/10]
          # A fixed, smoothed past directional rate and its exposure; no future counts.
          rates=(0..1).map{|j|[4,5*(switches[j]+1)/(exposures[j]+2)].min}
          support=(0..1).map{|j|case exposures[j];when 0 then 0;when 1..3 then 1;when 4..8 then 2;else 3;end}
          # Current-direction rate is primary. Opposite route is left for a later rival.
          directional=phase+[rates[a],support[a]]
          d=case duration;when 1 then 0;when 2 then 1;when 3..4 then 2;when 5..8 then 3;else 4;end
          keys=[base,obs,phase,directional,directional+[past],directional+[d],directional+[d,changed ? 1 : 0]]
          [id[0],id.take(3),keys,(a-Integer(rs[i+1]['RouteA'])).abs]
        end
      end
    end
    def tables
      Array.new(MODES.size){Hash.new{|h,k|h[k]=[0,0]}}
    end
    def fit(rows)
      all=tables;held=Hash.new{|h,k|h[k]=tables}
      rows.each do |sid,_,ks,y|
        raise 'invalid record' unless ks.size==MODES.size && [0,1].include?(y)
        ks.each_with_index{|k,i|[all[i][k],held[sid][i][k]].each{|v|v[0]+=1;v[1]+=y}}
      end
      [all,held]
    end
    def probabilities(counts,strength)
      raise ArgumentError,'strength' unless strength>0
      out=[]
      counts.each_with_index do |(n,y),i|
        out<<(i==0 ? (y+1.0)/(n+2) : (y+strength*out[PARENTS[i]])/(n+strength))
      end
      out
    end
    def predict(ks,all,held,strength:12)
      counts=ks.each_with_index.map{|k,i|all[i][k].zip(held[i][k]).map{|a,b|a-b}}
      probabilities(counts,strength)
    end
    def evaluate(rows,strength:12)
      all,held=fit(rows);raise 'need two sessions' unless held.size>=2
      folds=Hash.new{|h,k|h[k]=Array.new(MODES.size){[0,0.0,0.0]}}
      groups=Hash.new{|h,k|h[k]=Array.new(MODES.size){[0,0.0,0.0]}}
      strata=Hash.new{|h,k|h[k]=Array.new(MODES.size){[0,0.0,0.0]}}
      rows.each do |sid,g,ks,y|
        predict(ks,all,held.fetch(sid),strength:strength).each_with_index do |p,i|
          loss=-Math.log(y==1 ? p : 1-p);brier=(p-y)**2
          [folds[sid][i],groups[g][i],strata[[ks[0][2],ks[2].last]][i]].each{|v|v[0]+=1;v[1]+=loss;v[2]+=brier}
        end
      end
      scores=MODES.each_with_index.to_h do |m,i|
        vs=folds.values.map{|v|v[i]};gs=groups.values.map{|v|v[i]}
        [m,{session_logloss:vs.sum{|n,l,_|l/n}/vs.size,group_logloss:gs.sum{|n,l,_|l/n}/gs.size,session_brier:vs.sum{|n,_,b|b/n}/vs.size}]
      end
      ds=folds.values.map{|v|v[5][1]/v[5][0]-v[4][1]/v[4][0]}
      {sessions:held.size,groups:groups.size,records:rows.size,strength:strength,scores:scores,duration_minus_recent:{mean:ds.sum/ds.size,better:ds.count(&:negative?),delete_one_score_range:ds.map{|x|(ds.sum-x)/(ds.size-1)}.minmax},strata:strata.sort.map{|(a,phase),v|{route:a,phase:phase,n:v[0][0],duration_minus_recent:(v[5][1]-v[4][1])/v[0][0]}}}
    end
    def audit(path,strength:12)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      evaluate(records(rows),strength:strength).merge(source_sha256:s::SHA,aggregate_only:true)
    end
  end
end
puts JSON.pretty_generate(RithmT28::Hazard.audit(ARGV.fetch(0),strength:Float(ARGV.fetch(1,'12')))) if $PROGRAM_NAME==__FILE__
