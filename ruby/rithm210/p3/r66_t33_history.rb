# frozen_string_literal: true
require_relative 'r66_t26_source_contract'
module RithmT33
  module History
    MODES=[:occupancy,:treatment,:phase,:lag,:turnover,:history].freeze
    PARENTS=[nil,0,1,2,2,3].freeze
    module_function
    # Analyst-visible group histories; not assumed available to uninformed actors.
    def records(rows,periods:40)
      rows.group_by{|r|r.values_at('session','Group','trt')}.flat_map do |id,rs|
        times=rs.group_by{|r|Integer(r['Period'])};raise 'incomplete group' unless times.keys.sort==(1..periods).to_a
        states=times.transform_values do |v|
          a=v.to_h{|r|[r['ID'],Integer(r['RouteA'])]};raise 'group routes' unless v.size==6 && a.size==6 && a.values.all?{|x|[0,1].include?(x)}
          a
        end
        (2...periods).map do |t|
          prev=states.fetch(t-1);now=states.fetch(t);n=now.values.sum;lag=prev.values.sum
          raise 'actor mismatch' unless now.keys.sort==prev.keys.sort && now.keys.sort==states.fetch(t+1).keys.sort
          count=now.count{|k,v|prev.fetch(k)!=v};bucket=[count,3].min
          b=[n];tr=b+[id[2]];phase=tr+[(t-1)/10]
          [id.first,[b,tr,phase,phase+[lag],phase+[bucket],phase+[lag,bucket]],states.fetch(t+1).values.sum]
        end
      end
    end
    def tables
      Array.new(MODES.size){Hash.new{|h,k|h[k]=Array.new(7,0)}}
    end
    def fit(records)
      all=tables;held=Hash.new{|h,k|h[k]=tables}
      records.each do |sid,ks,y|
        raise 'invalid record' unless ks.size==MODES.size && y.is_a?(Integer) && y.between?(0,6)
        ks.each_with_index{|k,i|all[i][k][y]+=1;held[sid][i][k][y]+=1}
      end
      [all,held]
    end
    def predict(ks,all,held,strength:12)
      raise ArgumentError,'strength' unless strength.finite? && strength>0
      out=[];ks.each_with_index do |k,i|
        counts=all[i][k].zip(held[i][k]).map{|a,b|a-b};n=counts.sum
        prior=i==0 ? Array.new(7,1.0/7) : out[PARENTS[i]]
        mass=i==0 ? 7.0 : strength
        out<<counts.each_with_index.map{|v,j|(v+mass*prior[j])/(n+mass)}
      end;out
    end
    def evaluate(records,strength:12)
      all,held=fit(records);raise 'need two sessions' unless held.size>=2
      folds=Hash.new{|h,k|h[k]=Array.new(MODES.size){[0,0.0,0.0,0.0]}}
      records.each do |sid,ks,y|
        predict(ks,all,held.fetch(sid),strength:strength).each_with_index do |q,i|
          v=folds[sid][i];v[0]+=1;v[1]-=Math.log(q[y]);v[2]+=q.each_with_index.sum{|p,k|p*3*(k-4)**2};v[3]+=3*(y-4)**2
        end
      end
      scores=MODES.each_with_index.to_h do |m,i|
        vs=folds.values.map{|v|v[i]};[m,{logloss:vs.sum{|n,l,_,_|l/n}/vs.size,cost:vs.sum{|n,_,c,_|c/n}/vs.size,actual:vs.sum{|n,_,_,c|c/n}/vs.size}]
      end
      contrasts=[[2,3],[2,4],[2,5],[3,5]].to_h do |i,j|
        d=folds.values.map{|v|v[j][1]/v[j][0]-v[i][1]/v[i][0]};["#{MODES[j]}_minus_#{MODES[i]}",{mean:d.sum/d.size,better:d.count(&:negative?)}]
      end
      {sessions:held.size,targets:records.size,strength:strength,scores:scores,contrasts:contrasts}
    end
    def audit(path)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      rs=records(rows);{models:[3,12,48].map{|v|evaluate(rs,strength:v)},source_sha256:s::SHA,aggregate_only:true}
    end
  end
end
puts JSON.pretty_generate(RithmT33::History.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
