# frozen_string_literal: true
require_relative 'r66_t38_fiber'
module RithmT38
  module Oracle
    F=Fiber
    module_function
    # Uniformly bound regret with exact event probability observed. In each
    # bin, allow both adversarial worlds to be anywhere in that bin.
    def bounds(s,idx,bins:64)
      raise ArgumentError,'bins' unless bins.is_a?(Integer) && bins>0
      vs=s[:vertices];x,y=vs.map{|q|F.event(q,idx)}.minmax
      return [risk(s,*vs.minmax_by(&:first))]*2 if x==y
      knots=(0..bins).map{|i|x+(y-x)*i/bins}
      knots=(knots+vs.map{|q|F.event(q,idx)}).uniq.sort
      slices=knots.map{|z|F.slice(vs,idx,z)}
      lo=slices.map{|a,b|risk(s,a,b)}.max
      hi=knots.each_cons(2).with_index.map do |(a,b),i|
        v=slices[i]+slices[i+1]+vs.select{|q|F.event(q,idx).between?(a,b)}
        risk(s,*v.minmax_by(&:first))
      end.max
      [lo,hi]
    end
    def risk(s,low,high)
      a=s[:baseline]-F.cost_and_slope(high.first,s[:mean_cost],F::REC,F::H).first
      b=F.cost_and_slope(low.first,s[:mean_cost],F::REC,F::H).first-s[:baseline]
      a>0 && b>0 ? F.harm_floor(a,b) : 0r
    end
    def audit
      s=F.setup;events={'no_switch'=>[0],'two_or_more'=>[2,3,4,5],'all_five'=>[5]}
      {synthetic_only:true,reference:'exact event probability observed; all stationary laws on T33 exchangeable moment fiber',results:events.transform_values{|idx|[16,64,256].map{|n|l,u=bounds(s,idx,bins:n);{bins:n,lower:l.to_f,upper:u.to_f}}}}
    end
  end
end
puts JSON.pretty_generate(RithmT38::Oracle.audit) if $PROGRAM_NAME==__FILE__
