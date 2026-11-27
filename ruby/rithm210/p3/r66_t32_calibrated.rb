# frozen_string_literal: true
require_relative 'r66_t30_group'
require_relative 'r66_t31_coupling'
module RithmT32
  module Calibrated
    G=RithmT30::Group; P=G::P; M=G::M
    GRID=[0.0,-0.1,0.1,-0.2,0.2].product([1.0,0.75,1.25]).freeze
    WEIGHTS=[0.0,-0.025,0.025,-0.1,0.1,-0.25,0.25].freeze
    module_function
    def split(sessions,outer,n)
      raise ArgumentError,'split' unless sessions.uniq.size==sessions.size && sessions.include?(outer) && n.is_a?(Integer) && n.between?(1,sessions.size-2)
      ordered=sessions.sort; i=ordered.index(outer)
      rest=ordered.rotate(i+1).reject{|s|s==outer};[rest.drop(n),rest.take(n)]
    end
    def transform(p,offset,slope)
      raise ArgumentError,'calibration inputs' unless p.finite? && p.between?(0,1) && offset.finite? && slope.finite? && slope>0
      return p if p==0 || p==1 || (offset==0 && slope==1)
      z=offset+slope*Math.log(p/(1-p));z>=0 ? 1/(1+Math.exp(-z)) : Math.exp(z)/(1+Math.exp(z))
    end
    def fit(data,train,iterations)
      data.select{|r|train.include?(r[0])}.group_by{|r|r[1]}.transform_values{|v|M.fit(v.map(&:last),iterations:iterations)}
    end
    def groups(data,sid,fits)
      groups=Hash.new{|h,k|h[k]=[[],[]]}
      data.select{|r|r[0]==sid}.each do |_,key,ev,g,ps,_|
        w=fits[key]||Array.new(M::TYPES.size,1.0/M::TYPES.size)
        P.predict(ev,ps,w).each_with_index do |p,i|
          next if i==0
          a,_,y=ev[i];v=groups[g+[i]];v[0]<<(a==1 ? 1-p : p);v[1]<<(a==1 ? 1-y : y)
        end
      end
      raise 'invalid group targets' if groups.empty? || groups.values.any?{|p,a|p.size!=6 || a.size!=6}
      groups.values
    end
    def extremes(ps)
      mu=ps.sum;k=mu.floor;f=mu-k;lo=Array.new(7,0.0);lo[k]=1-f;lo[k+1]=f if k<6
      desc=ps.sort.reverse;hi=[1-desc.first]+desc.each_cons(2).map{|a,b|a-b}+[desc.last]
      [lo,hi]
    end
    def laws(ps)
      [G.occupancy(ps),*extremes(ps)]
    end
    def joint(q,w)
      base,lo,hi=q;other=w<0 ? lo : hi
      base.zip(other).map{|a,b|(1-w.abs)*a+w.abs*b}
    end
    def score(rows,offset,slope,w)
      raise 'empty targets' if rows.empty?
      sums=Hash.new(0.0)
      rows.each do |ps,a|
        p=ps.map{|x|transform(x,offset,slope)};q=joint(laws(p),w);n=a.sum
        p.zip(a).each{|x,y|sums[:individual_logloss]-=Math.log(y==1 ? x : 1-x);sums[:individual_brier]+=(y-x)**2}
        sums[:group_logloss]-=Math.log(q[n]);sums[:predicted_cost]+=q.each_with_index.sum{|x,k|x*3*(k-4)**2};sums[:actual_cost]+=3*(n-4)**2
        sums[:pair_residual]+=a.zip(p).map{|x,y|x-y}.combination(2).sum{|x,y|x*y}/15.0
      end
      sums.transform_keys(&:to_sym).to_h{|k,v|[k,v/(k.to_s.start_with?('individual') ? rows.size*6 : rows.size)]}
    end
    def marginal_loss(rows,o,s)
      rows.sum do |ps,a|
        ps.zip(a).sum do |p,y|
          x=transform(p,o,s);-Math.log(y==1 ? x : 1-x)
        end
      end.fdiv(rows.size*6)
    end
    def joint_choice(cal,o,s)
      totals=Array.new(WEIGHTS.size,0.0)
      cal.each do |rows|
        fold=Array.new(WEIGHTS.size,0.0)
        rows.each do |ps,a|
          p=ps.map{|x|transform(x,o,s)};n=a.sum;base,lo,hi=laws(p).map{|q|q[n]}
          WEIGHTS.each_with_index do |w,i|
            fold[i]-=Math.log((1-w.abs)*base+w.abs*(w<0 ? lo : hi))
          end
        end
        fold.each_with_index{|v,i|totals[i]+=v/rows.size}
      end
      WEIGHTS[totals.each_index.min_by{|i|totals[i]}]
    end
    def select(cal)
      raise 'empty calibration' if cal.empty? || cal.any?(&:empty?)
      m=GRID.min_by{|o,s|cal.sum{|rows|marginal_loss(rows,o,s)}}
      [m,joint_choice(cal,0,1),joint_choice(cal,*m)]
    end
    def evaluate(paths,iterations:40,calibration_sessions:8)
      raise ArgumentError,'iterations' unless iterations.is_a?(Integer) && iterations>0
      data=paths.map{|sid,key,ev,g|raise 'group key' unless g && g.first==sid;[sid,key,ev,g,*P.prepare(ev,0.15,1.0)]}
      sessions=data.map(&:first).uniq.sort
      choices=Hash.new(0);folds=[]
      sessions.each do |outer|
        train,cal=split(sessions,outer,calibration_sessions);fits=fit(data,train,iterations)
        m,w0,w1=select(cal.map{|sid|groups(data,sid,fits)})
        rows=groups(data,outer,fits)
        choices[[*m,w0,w1]]+=1
        folds<<{base:score(rows,0,1,0),marginal:score(rows,*m,0),joint:score(rows,0,1,w0),both:score(rows,*m,w1),n:rows.size}
      end
      modes=[:base,:marginal,:joint,:both]
      {sessions:sessions.size,training_sessions:sessions.size-1-calibration_sessions,calibration_sessions:calibration_sessions,group_targets:folds.sum{|f|f[:n]},iterations:iterations,
       scores:modes.to_h{|mode|[mode,folds.first[mode].keys.to_h{|k|[k,folds.sum{|f|f[mode][k]}/folds.size]}]},
       group_better_than_base:modes.drop(1).to_h{|mode|[mode,folds.count{|f|f[mode][:group_logloss]<f[:base][:group_logloss]}]},
       selections:choices.map{|(o,s,w0,w1),n|{offset:o,slope:s,raw_joint:w0,calibrated_joint:w1,folds:n}}}
    end
    def audit(path,iterations:40,calibration_sessions:8)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      evaluate(P.trajectories(rows),iterations:iterations,calibration_sessions:calibration_sessions).merge(source_sha256:s::SHA,aggregate_only:true)
    end
  end
end
puts JSON.pretty_generate(RithmT32::Calibrated.audit(ARGV.fetch(0),iterations:Integer(ARGV.fetch(1,'40')),calibration_sessions:Integer(ARGV.fetch(2,'8')))) if $PROGRAM_NAME==__FILE__
