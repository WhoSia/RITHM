# frozen_string_literal: true
require_relative 'r66_t29_mixture'
require_relative 'r66_t26_forecast'
module RithmT30
  module Payoff
    M=RithmT29::Mixture;F=RithmT26::Forecast
    module_function
    # Equal weights on payoff-compatible states are a predictor, not identified beliefs.
    def gain(row)
      a=Integer(row['RouteA']);_,obs=F.keys(row,row).take(2);k=obs.last
      states=Integer(row['Informed'])==1 ? [k] : (0..5).select{|j|k[j]==1}
      (a==1 ? 1 : -1)*states.sum{|j|3*j-11}.fdiv(states.size)
    end
    def trajectories(rows,periods:40)
      rows.group_by{|r|r.values_at('session','Group','trt','ID')}.map do |id,rs|
        rs=rs.sort_by{|r|Integer(r['Period'])}
        raise 'incomplete trajectory' unless rs.map{|r|Integer(r['Period'])}==(1..periods).to_a
        a=rs.map{|r|Integer(r['RouteA'])};info=rs.map{|r|Integer(r['Informed'])}.uniq
        raise 'route/info' unless a.all?{|v|[0,1].include?(v)} && info.size==1 && [0,1].include?(info.first)
        first=true
        ev=M.events(a).each_with_index.map do |(route,d,y),i|
          event=[route,d,y,gain(rs[i]),first];first=false if y==1;event
        end
        [id.first,[id[2],info.first,a.first],ev]
      end
    end
    def probabilities(event,beta,multiplier,types=M::TYPES)
      a,d,_,g,first=event
      factor=Math.exp(beta*g)*(d>=3 && !first ? multiplier : 1)
      types.map{|type|p=type[a];factor*p/(1-p+factor*p)}
    end
    def prepare(ev,beta,multiplier,types=M::TYPES)
      ps=ev.map{|e|probabilities(e,beta,multiplier,types)}
      l=Array.new(types.size,1.0)
      ps.each_with_index{|p,i|p.each_with_index{|v,j|l[j]*=ev[i][2]==1 ? v : 1-v}}
      [ps,l]
    end
    def predict(ev,ps,w)
      w=w.dup
      ev.each_with_index.map do |e,i|
        p=0.0;ps[i].each_with_index{|v,j|p+=w[j]*v}
        z=0.0;ps[i].each_with_index{|v,j|w[j]*=e[2]==1 ? v : 1-v;z+=w[j]}
        w.map!{|v|v/z};p
      end
    end
    def score_folds(paths,beta:0.0,multiplier:1.0,iterations:40)
      raise ArgumentError,'parameters' unless beta.finite? && multiplier.finite? && multiplier>0 && iterations.is_a?(Integer) && iterations>0
      data=paths.map{|sid,key,ev|[sid,key,ev,*prepare(ev,beta,multiplier)]}
      sessions=data.map(&:first).uniq;raise 'need two sessions' unless sessions.size>=2
      folds=sessions.map do |sid|
        train=data.reject{|r|r.first==sid};fits=train.group_by{|r|r[1]}.transform_values{|v|M.fit(v.map(&:last),iterations:iterations)}
        n=0;loss=0.0;brier=0.0;by_info=Hash.new{|h,k|h[k]=[0,0.0,0.0]}
        data.select{|r|r.first==sid}.each do |_,key,ev,ps,_|
          w=fits[key]||Array.new(M::TYPES.size,1.0/M::TYPES.size)
          predict(ev,ps,w).zip(ev).drop(1).each do |p,e|
            y=e[2];l=-Math.log(y==1 ? p : 1-p);b=(p-y)**2;n+=1;loss+=l;brier+=b
            v=by_info[key[1]];v[0]+=1;v[1]+=l;v[2]+=b
          end
        end
        raise 'empty held targets' if n==0
        [n,loss/n,brier/n,by_info]
      end
      sessions.zip(folds).to_h
    end
    def evaluate(paths,beta:0.0,multiplier:1.0,iterations:40)
      folds=score_folds(paths,beta:beta,multiplier:multiplier,iterations:iterations).values
      {beta:beta,later_spell_multiplier:multiplier,iterations:iterations,sessions:folds.size,records:folds.sum(&:first),session_logloss:folds.sum{|x|x[1]}/folds.size,session_brier:folds.sum{|x|x[2]}/folds.size}
    end
    def audit(path,iterations:40)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      paths=trajectories(rows)
      models=[[-0.15,1.0],[0.0,1.0],[0.15,1.0],[0.3,1.0],[0.15,0.5],[0.15,2.0]].map{|b,m|evaluate(paths,beta:b,multiplier:m,iterations:iterations)}
      {models:models,source_sha256:s::SHA,aggregate_only:true}
    end
  end
end
puts JSON.pretty_generate(RithmT30::Payoff.audit(ARGV.fetch(0),iterations:Integer(ARGV.fetch(1,'40')))) if $PROGRAM_NAME==__FILE__
