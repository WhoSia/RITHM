# frozen_string_literal: true
require_relative 'r66_t35_span'
require_relative 'r66_t26_source_contract'
module RithmT36
  module PolicySpan
    S=RithmT35::Span; C=(0..6).map{|n|3*(n-4)**2}.freeze
    module_function
    # Generators of the linear span of deterministic state-feedback kernels.
    def generators(ps,c,feedback:false)
      raise ArgumentError,'empty actions' if ps.empty?
      ps.each{|p|S.validate(p,c)}
      return ps unless feedback
      base=ps.first
      [base,*ps.drop(1).flat_map{|p|base.each_index.map{|i|base.each_with_index.map{|r,j|i==j ? p[i] : r}}}]
    end
    def profile(ps,c,feedback:false)
      gs=generators(ps,c,feedback:feedback);b=[Array.new(c.size,1)];front=[]
      if S.rank(b+[c])>b.size
        b<<c;front<<c
      end
      ranks=[b.size]
      until front.empty?
        next_front=[]
        front.each{|v|gs.each do |p|
          w=S.apply(p,v)
          if S.rank(b+[w])>b.size
            b<<w;next_front<<w
          end
        end}
        break if next_front.empty?
        ranks<<b.size;front=next_front
      end
      {basis:b,ranks:ranks}
    end
    def equivalent?(ps,qs,c,feedback:false)
      raise ArgumentError,'action mismatch' unless ps.size==qs.size
      qs.each{|q|S.validate(q,c)}
      profile(ps,c,feedback:feedback)[:basis].all?{|v|ps.zip(qs).all?{|p,q|S.apply(p,v)==S.apply(q,v)}}
    end
    # Known open-loop schedule; costs include the initial and every subsequent state.
    def schedule(ps,c,actions)
      actions.reverse_each.reduce(c){|v,a|c.zip(S.apply(ps.fetch(a),v)).map{|x,y|x+y}}
    end
    def fiber(a,b,n=6)
      raise ArgumentError,'occupancy' unless [a,b].all?{|x|x.is_a?(Integer)&&x.between?(0,n)}
      [(a-b).abs,[a+b,2*n-a-b].min]
    end
    def audit(path)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check.values_at(:rows,:sessions,:group_transitions)==[34560,24,5616]
      counts=Hash.new{|h,k|h[k]=Array.new(7){Array.new(7,0)}}
      state=Array.new(7){Hash.new(0)}; totals=Hash.new(0)
      rows.group_by{|r|r.values_at('session','Group','trt','Period')}.each do |(_,_,t,k),rs|
        next if k.to_i==40
        a,b,g=rs.first.values_at('NumA','NumAnext','NumSwitchWill').map(&:to_i);lo,hi=fiber(a,b)
        raise 'fiber violation' unless g.between?(lo,hi)&&(g-lo).even?
        counts[t][a][b]+=1;counts['all'][a][b]+=1
        [state[a],totals].each do |x|
          x[:transitions]+=1;x[:switches]+=g;x[:minimum_switches]+=lo;x[:maximum_switches]+=hi
          x[:unchanged_occupancy]+=1 if a==b;x[:no_switch]+=1 if g==0
          x[:hidden_turnover]+=g-lo
        end
      end
      mat=lambda{|ct|ct.map{|r|r.map{|x|Rational(x+1,r.sum+7)}}}
      ps=%w[1 2 3].map{|t|mat.call(counts[t])};p=mat.call(counts['all'])
      obs=[Array.new(7,1),(0..6).to_a,(0..6).map{|i|i*i}]
      cases={'pooled'=>profile([p],C),'treatment_indexed_open_loop'=>profile(ps,C),'treatment_indexed_feedback'=>profile(ps,C,feedback:true)}
      {source_sha256:s::SHA,aggregate_only:true,sessions:check[:sessions],totals:totals,by_start:state,
       profiles:cases.transform_values{|x|{ranks:x[:ranks],extra_measurements:S.deficit(obs,x[:basis])}},
       individual_treatment_ranks:ps.map{|q|profile([q],C)[:ranks]}}
    end
  end
end
puts JSON.pretty_generate(RithmT36::PolicySpan.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
