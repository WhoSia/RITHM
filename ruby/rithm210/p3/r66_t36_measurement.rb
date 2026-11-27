# frozen_string_literal: true
require_relative 'r66_t36_policy_span'
module RithmT36
  module Measurement
    P=PolicySpan;S=P::S
    module_function
    # Enumerate exact basic feasible solutions of Aq=b, q>=0.
    def vertices(a,b)
      n=a.first.size;k=S.rank(a);out=[]
      (0...n).to_a.combination(k) do |idx|
        m=a.zip(b).map{|r,v|idx.map{|i|Rational(r[i])}+[Rational(v)]};j=0
        k.times do |col|
          i=(j...m.size).find{|l|m[l][col]!=0};break unless i
          m[i],m[j]=m[j],m[i];d=m[j][col];m[j].map!{|v|v/d}
          m.each_index{|l|next if l==j;d=m[l][col];m[l]=m[l].zip(m[j]).map{|x,y|x-d*y} if d!=0};j+=1
        end
        next unless j==k
        q=Array.new(n,0r);idx.each_with_index{|i,l|q[i]=m[l].last}
        out<<q if q.all?{|v|v>=0} && S.apply(a,q)==b
      end
      raise ArgumentError,'empty fiber' if out.empty?
      out.uniq
    end
    def width(vs,v)
      l,h=vs.map{|q|S.dot(q,v)}.minmax;h-l
    end
    def audit(path)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check.values_at(:rows,:sessions,:group_transitions)==[34560,24,5616]
      ct=Array.new(7){Array.new(7,0)}
      rows.group_by{|r|r.values_at('session','Group','trt','Period')}.each do |(_,_,_,t),rs|
        next if t.to_i==40
        a,b=rs.first.values_at('NumA','NumAnext').map(&:to_i);ct[a][b]+=1
      end
      p=ct.map{|r|r.map{|x|Rational(x+1,r.sum+7)}};base=[Array.new(7,1),(0..6).to_a,(0..6).map{|n|n*n}]
      total=ct.sum(&:sum); horizons=[2,5,20];results=horizons.map do |h|
        v=S.values(p,P::C,h-1);per=p.each_with_index.map do |q,i|
          candidates={'none'=>nil,'third_moment'=>(0..6).map{|n|n**3},'no_net_change'=>(0..6).map{|n|n==i ? 1 : 0},'efficient_next'=>(0..6).map{|n|n==4 ? 1 : 0},'low_occupancy'=>(0..6).map{|n|n<=2 ? 1 : 0},'high_occupancy'=>(0..6).map{|n|n>=5 ? 1 : 0},'value_target'=>v}
          candidates.transform_values do |x|
            a=x ? base+[x] : base; width(vertices(a,S.apply(a,q)),v)
          end
        end
        avg=per.first.keys.to_h{|k|[k,per.each_with_index.sum{|r,i|r[k]*ct[i].sum}.fdiv(total)]}
        natural=per.first.keys-['none','value_target'];best=per.map{|r|natural.min_by{|k|r[k]}}
        {horizon:h,weighted_width:avg,state_adaptive_width:per.each_with_index.sum{|r,i|r[best[i]]*ct[i].sum}.fdiv(total),state_adaptive_choice:best}
      end
      {source_sha256:s::SHA,aggregate_only:true,reference:'pooled smoothed empirical Markov, only first row uncertain; fixed downstream reference',sessions:check[:sessions],transitions:total,results:results}
    end
  end
end
puts JSON.pretty_generate(RithmT36::Measurement.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
