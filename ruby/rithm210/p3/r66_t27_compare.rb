# frozen_string_literal: true
require_relative 'r66_t27_features'
module RithmT27
  module Compare
    F=Features
    CONTRASTS=[[3,4],[3,5],[1,6],[3,7],[7,8]].freeze
    module_function
    def tables
      Array.new(F::MODES.size){Hash.new{|h,k|h[k]=[0,0]}}
    end
    def fit(records)
      all=tables;held=Hash.new{|h,k|h[k]=tables}
      records.each do |sid,ks,y|
        raise 'record' unless ks.size==F::MODES.size && [0,1].include?(y)
        ks.each_with_index{|k,i|[all[i][k],held[sid][i][k]].each{|v|v[0]+=1;v[1]+=y}}
      end
      [all,held]
    end
    def predict(ks,all,held,strength:12,omitted:nil)
      raise ArgumentError,'strength' unless strength>0
      out=[]
      ks.each_with_index do |k,i|
        # With full disclosure, the filter contains no additional historical information.
        if [6,8].include?(i) && ks[0][1]==1
          out<<out[F::PARENTS[i]];next
        end
        n,y=all[i][k].zip(held[i][k]).map{|a,b|a-b}
        if omitted
          a,b=omitted[i][k];n-=a;y-=b
        end
        out<< (i==0 ? (y+1.0)/(n+2) : (y+strength*out[F::PARENTS[i]])/(n+strength))
      end
      out
    end
    def evaluate(records,strength:12)
      all,held=fit(records);raise 'need at least two sessions' unless held.size>=2
      folds=held.keys.to_h{|sid|[sid,Array.new(F::MODES.size){[0,0.0,0.0]}]}
      # Repeated feature keys in a held session have identical training predictions.
      cache={}
      records.each do |sid,ks,y|
        ps=cache[[sid,ks]]||=predict(ks,all,held.fetch(sid),strength:strength)
        ps.each_with_index do |p,i|
          v=folds.fetch(sid)[i];v[0]+=1;v[1]-=Math.log(y==1 ? p : 1-p);v[2]+=(p-y)**2
        end
      end
      scores=F::MODES.each_with_index.to_h do |mode,i|
        vs=folds.values.map{|v|v[i]};n=vs.sum(&:first)
        [mode,{n:n,session_logloss:vs.sum{|v|v[1]/v[0]}/vs.size,session_brier:vs.sum{|v|v[2]/v[0]}/vs.size}]
      end
      contrasts=CONTRASTS.to_h do |i,j|
        d=folds.values.map{|v|(v[j][1]-v[i][1])/v[i][0]};m=d.sum/d.size
        loo=d.map{|x|(d.sum-x)/(d.size-1)}
        ["#{F::MODES[j]}_minus_#{F::MODES[i]}",{mean:m,better:d.count(&:negative?),delete_one_score_range:loo.minmax}]
      end
      {sessions:held.size,records:records.size,strength:strength,scores:scores,contrasts:contrasts}
    end
    def audit(path,rho:0.5,strength:12)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      evaluate(F.records(rows,rho:rho),strength:strength).merge(rho:rho,source_sha256:s::SHA,aggregate_only:true)
    end
  end
end
puts JSON.pretty_generate(RithmT27::Compare.audit(ARGV.fetch(0),rho:Float(ARGV.fetch(1,'0.5')),strength:Float(ARGV.fetch(2,'12')))) if $PROGRAM_NAME==__FILE__
