# frozen_string_literal: true
require_relative 'r66_t26_source_contract'
module RithmT38
  module Empirical
    S=RithmT26::SourceContract
    module_function
    def histogram(rows)
      # T26 independently checks next-period chronology and lead columns first.
      h=Hash.new{|a,k|a[k]=Array.new(6,0)}
      rows.group_by{|r|r.values_at('session','Group','trt','Period')}.each do |(sid,_,t,k),rs|
        next if Integer(k)==40 || Integer(rs.first['NumA'])!=5
        m=rs.sum{|r|Integer(r['switchAtoBWill'])}
        raise 'departure count' unless m.between?(0,5)
        h[[sid,t]][m]+=1
      end
      h
    end
    def stats(c)
      n=c.sum;raise ArgumentError,'empty exposure' if n==0
      p=c.each_with_index.sum{|v,i|v*i}.fdiv(5*n)
      t=c.each_with_index.sum{|v,i|v*i*(i-1)}.fdiv(20*n)
      {n:n,p:p,pair:t,pair_residual:t-p*p,no_departure:c[0].fdiv(n),two_or_more:c.drop(2).sum.fdiv(n),all_five:c[5].fdiv(n)}
    end
    def summarize(h,sessions,reps:2000,seed:3802)
      raise ArgumentError,'sessions/reps' unless sessions.size>=2 && sessions.uniq.size==sessions.size && reps.is_a?(Integer) && reps>0
      zero=Array.new(6,0);modes=%w[all 1 2 3]
      per=modes.to_h do |mode|
        [mode,sessions.map{|sid|mode=='all' ? %w[1 2 3].map{|t|h.fetch([sid,t],zero)}.transpose.map(&:sum) : h.fetch([sid,mode],zero)}]
      end
      rng=Random.new(seed);draws=Array.new(reps){Array.new(sessions.size){rng.rand(sessions.size)}}
      per.transform_values do |cs|
        c=cs.transpose.map(&:sum);point=stats(c);keys=point.keys-[:n]
        boot=draws.filter_map{|ix|v=ix.map{|i|cs[i]}.transpose.map(&:sum);stats(v) if v.sum>0}
        intervals=keys.to_h do |k|
          a=boot.map{|x|x[k]}.sort
          [k,[a[((a.size-1)*0.025).floor],a[((a.size-1)*0.975).ceil]]]
        end
        {counts:c,point:point,cluster_percentile95:intervals,valid_bootstrap_draws:boot.size}
      end
    end
    def audit(path)
      rows=S.read_rows(path);check=S.summarize(rows)
      raise 'cohort mismatch' unless check.values_at(:rows,:sessions,:group_transitions)==[34560,24,5616]
      h=histogram(rows);sessions=rows.map{|r|r['session']}.uniq.sort
      {source_sha256:S::SHA,aggregate_only:true,sessions:sessions.size,reference:'old occupancy A=5, A-to-B departure count only; session cluster bootstrap descriptive, not T33 intervention fit',results:summarize(h,sessions)}
    end
  end
end
puts JSON.pretty_generate(RithmT38::Empirical.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
