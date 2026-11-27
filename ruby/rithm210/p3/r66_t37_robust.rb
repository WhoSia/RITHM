# frozen_string_literal: true
require_relative 'r66_t36_measurement'
module RithmT37
  module Robust
    M=RithmT36::Measurement; S=M::S; C=M::P::C
    NAMES=%w[none third_moment no_net_change efficient_next low_occupancy high_occupancy].freeze
    module_function
    def bounds(fibers,c,h)
      raise ArgumentError,'dimensions/horizon' unless !c.empty? && fibers.size==c.size && h.is_a?(Integer) && h>=1
      fibers.each{|vs|raise ArgumentError,'fiber' if vs.empty? || vs.any?{|q|q.size!=c.size || q.any?(&:negative?) || q.sum!=1}}
      lo=hi=c
      (1...h).each do
        lo=c.each_with_index.map{|v,i|v+fibers[i].map{|q|S.dot(q,lo)}.min}
        hi=c.each_with_index.map{|v,i|v+fibers[i].map{|q|S.dot(q,hi)}.max}
      end
      [lo,hi]
    end
    def fibers(p,name)
      n=p.size; base=[Array.new(n,1),(0...n).to_a,(0...n).map{|i|i*i}]
      raise ArgumentError,'candidate' unless NAMES.include?(name)
      p.each_with_index.map do |q,i|
        z=case name
          when 'third_moment' then (0...n).map{|j|j**3}
          when 'no_net_change' then (0...n).map{|j|j==i ? 1 : 0}
          when 'efficient_next' then (0...n).map{|j|j==4 ? 1 : 0}
          when 'low_occupancy' then (0...n).map{|j|j<=2 ? 1 : 0}
          when 'high_occupancy' then (0...n).map{|j|j>=5 ? 1 : 0}
        end
        a=z ? base+[z] : base;M.vertices(a,S.apply(a,q))
      end
    end
    def audit(path)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check.values_at(:rows,:sessions,:group_transitions)==[34560,24,5616]
      ct=Array.new(7){Array.new(7,0)}
      rows.group_by{|r|r.values_at('session','Group','trt','Period')}.each do |(_,_,_,t),rs|
        next if t.to_i==40
        a,b=rs.first.values_at('NumA','NumAnext').map(&:to_i);ct[a][b]+=1
      end
      p=ct.map{|r|r.map{|x|Rational(x+1,r.sum+7)}};w=ct.map{|r|Rational(r.sum,ct.sum(&:sum))}
      results=NAMES.to_h do |name|
        fs=fibers(p,name)
        [name,[2,5,20,40].map do |h|
          lo,hi=bounds(fs,C,h);v=S.values(p,C,h-1)
          # Attained fixed-law witnesses; not stationary extrema in general.
          a=fs.map{|vs|vs.min_by{|q|S.dot(q,v)}};b=fs.map{|vs|vs.max_by{|q|S.dot(q,v)}}
          l,u=[a,b].map{|q|S.dot(w,S.values(q,C,h))}.minmax
          {horizon:h,lower:S.dot(w,lo).to_f,upper:S.dot(w,hi).to_f,width:S.dot(w,hi.zip(lo).map{|x,y|x-y}).to_f,stationary_witness_width:(u-l).to_f}
        end]
      end
      {source_sha256:s::SHA,aggregate_only:true,sessions:24,transitions:5616,reference:'all rows uncertain, exact reference moments, row/time rectangular; fixed-law witnesses only',results:results}
    end
  end
end
puts JSON.pretty_generate(RithmT37::Robust.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
