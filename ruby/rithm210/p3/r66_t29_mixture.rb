# frozen_string_literal: true
require_relative 'r66_t26_source_contract'
module RithmT29
  module Mixture
    GRID=[0.05,0.2,0.5,0.8,0.95].freeze
    TYPES=GRID.product(GRID).freeze
    module_function
    def trajectories(rows,periods:40)
      rows.group_by{|r|r.values_at('session','Group','trt','ID')}.map do |id,rs|
        rs=rs.sort_by{|r|Integer(r['Period'])}
        raise 'incomplete trajectory' unless rs.map{|r|Integer(r['Period'])}==(1..periods).to_a
        a=rs.map{|r|Integer(r['RouteA'])};info=rs.map{|r|Integer(r['Informed'])}.uniq
        raise 'route/info' unless a.all?{|v|[0,1].include?(v)} && info.size==1 && [0,1].include?(info.first)
        [id.first,[id[2],info.first],a]
      end
    end
    def probability(p,duration,multiplier)
      return p if duration<3
      multiplier*p/(1-p+multiplier*p)
    end
    def events(routes)
      duration=1
      routes.each_cons(2).map do |a,b|
        y=(a-b).abs;event=[a,duration,y];duration=y==1 ? 1 : duration+1;event
      end
    end
    def likelihood(ev,multiplier,types=TYPES)
      types.map do |type|
        ev.reduce(1.0){|l,(a,d,y)|p=probability(type[a],d,multiplier);l*(y==1 ? p : 1-p)}
      end
    end
    # Fixed support and positive pseudo-counts: regularized mixture weights, not NPML over support.
    def fit(likelihoods,iterations:100,pseudo:0.05)
      raise ArgumentError,'fit inputs' unless !likelihoods.empty? && iterations>0 && pseudo>0
      k=likelihoods.first.size;w=Array.new(k,1.0/k)
      raise ArgumentError,'likelihood rows' unless k>0 && likelihoods.all?{|l|l.size==k && l.all?{|x|x.finite? && x>=0} && l.sum>0}
      iterations.times do
        c=Array.new(k,pseudo)
        likelihoods.each do |l|
          z=0.0;k.times{|j|z+=w[j]*l[j]}
          k.times{|j|c[j]+=w[j]*l[j]/z}
        end
        sum=c.sum;w=c.map{|v|v/sum}
      end
      w
    end
    def predict(ev,w,multiplier,types=TYPES)
      w=w.dup
      ev.map do |a,d,y|
        ps=types.map{|type|probability(type[a],d,multiplier)}
        p=w.zip(ps).sum{|x,b|x*b}
        updated=w.zip(ps).map{|x,b|x*(y==1 ? b : 1-b)};z=updated.sum
        w=updated.map{|x|x/z}
        p
      end
    end
    def evaluate(paths,multiplier:1.0,condition_initial:true,iterations:100)
      raise ArgumentError,'multiplier' unless multiplier.finite? && multiplier>0
      data=paths.map do |sid,stratum,routes|
        ev=events(routes);key=condition_initial ? stratum+[routes.first] : stratum
        [sid,key,ev,likelihood(ev,multiplier)]
      end
      sessions=data.map(&:first).uniq;raise 'need two sessions' unless sessions.size>=2
      scores=sessions.map do |sid|
        train=data.reject{|r|r.first==sid};fits=train.group_by{|r|r[1]}.transform_values{|v|fit(v.map(&:last),iterations:iterations)}
        n=0;loss=0.0;brier=0.0
        data.select{|r|r.first==sid}.each do |_,key,ev,_|
          w=fits[key]||Array.new(TYPES.size,1.0/TYPES.size)
          predict(ev,w,multiplier).zip(ev).drop(1).each do |p,(_,_,y)|
            n+=1;loss-=Math.log(y==1 ? p : 1-p);brier+=(p-y)**2
          end
        end
        raise 'empty held targets' if n==0
        [n,loss/n,brier/n]
      end
      {sessions:sessions.size,records:scores.sum(&:first),session_logloss:scores.sum{|x|x[1]}/scores.size,session_brier:scores.sum{|x|x[2]}/scores.size}
    end
    def audit(path,iterations:100)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      paths=trajectories(rows)
      models=[[1.0,false],[1.0,true],[0.5,true],[2.0,true]].map{|m,c|evaluate(paths,multiplier:m,condition_initial:c,iterations:iterations).merge(multiplier:m,condition_initial:c)}
      {models:models,iterations:iterations,source_sha256:s::SHA,aggregate_only:true}
    end
  end
end
puts JSON.pretty_generate(RithmT29::Mixture.audit(ARGV.fetch(0),iterations:Integer(ARGV.fetch(1,'100')))) if $PROGRAM_NAME==__FILE__
