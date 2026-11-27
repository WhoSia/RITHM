# frozen_string_literal: true
require_relative 'r66_t30_payoff'
module RithmT30
  module Group
    P=Payoff;M=P::M
    module_function
    def occupancy(ps)
      raise ArgumentError,'six probabilities' unless ps.size==6 && ps.all?{|p|p.finite? && p.between?(0,1)}
      ps.reduce([1.0]) do |old,p|
        q=Array.new(old.size+1,0.0)
        old.each_with_index{|x,i|q[i]+=x*(1-p);q[i+1]+=x*p};q
      end
    end
    def metrics(ps,actual)
      raise ArgumentError,'six binary outcomes' unless actual.size==6 && actual.all?{|a|[0,1].include?(a)}
      q=occupancy(ps);n=actual.sum;mean=ps.sum;res=actual.zip(ps).map{|a,p|a-p}
      {logloss:-Math.log(q[n]),actual_cost:3*(n-4)**2,predicted_cost:q.each_with_index.sum{|x,k|x*3*(k-4)**2},occupancy_squared_error:(n-mean)**2,independent_variance:ps.sum{|p|p*(1-p)},pair_residual:res.combination(2).sum{|x,y|x*y}/15.0}
    end
    def evaluate(paths,beta:,iterations:40)
      raise ArgumentError,'beta/iterations' unless beta.finite? && iterations.is_a?(Integer) && iterations>0
      data=paths.map{|sid,key,ev,g|raise 'missing group key' unless g && g.first==sid;[sid,key,ev,g,*P.prepare(ev,beta,1.0)]}
      sessions=data.map(&:first).uniq;raise 'need two sessions' unless sessions.size>=2
      folds=sessions.map do |sid|
        train=data.reject{|r|r.first==sid};fits=train.group_by{|r|r[1]}.transform_values{|v|M.fit(v.map(&:last),iterations:iterations)}
        groups=Hash.new{|h,k|h[k]=[[],[]]}
        data.select{|r|r.first==sid}.each do |_,key,ev,g,ps,_|
          w=fits[key]||Array.new(M::TYPES.size,1.0/M::TYPES.size)
          P.predict(ev,ps,w).each_with_index do |p,i|
            next if i==0
            a,_,y=ev[i];v=groups[g+[i]];v[0]<<(a==1 ? 1-p : p);v[1]<<(a==1 ? 1-y : y)
          end
        end
        values=groups.values.map{|ps,actual|metrics(ps,actual)};raise 'empty group targets' if values.empty?
        [values.size,values.first.keys.to_h{|k|[k,values.sum{|v|v[k]}.fdiv(values.size)]}]
      end
      {beta:beta,iterations:iterations,sessions:folds.size,group_targets:folds.sum(&:first),session_mean:folds.first.last.keys.to_h{|k|[k,folds.sum{|v|v.last[k]}.fdiv(folds.size)]}}
    end
    def audit(path)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      paths=P.trajectories(rows);{models:[0.0,0.15].map{|b|evaluate(paths,beta:b)},source_sha256:s::SHA,aggregate_only:true}
    end
  end
end
puts JSON.pretty_generate(RithmT30::Group.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
