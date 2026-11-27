# frozen_string_literal: true
require 'json'
require_relative 'r66_t33_recurrent'
module RithmT37
  module Regret
    R=RithmT33::Recurrent
    module_function
    def binomial(p,n)
      raise ArgumentError,'probability/sample size' unless p.between?(0,1) && n.is_a?(Integer) && n>=0
      p=Rational(p);comb=1
      (0..n).map do |k|
        v=comb*p**k*(1-p)**(n-k);comb=comb*(n-k)/(k+1);v
      end
    end
    # Two-world randomized minimax decision, exact likelihood-ratio threshold.
    # Action 1 is preferable in world A, action 0 in world B.
    def solve(a,b,loss_a,loss_b)
      raise ArgumentError,'laws/losses' unless a.size==b.size && [a,b].all?{|v|v.sum==1 && v.all?{|x|x>=0}} && loss_a>0 && loss_b>0
      x=loss_a;y=0r;policy=Array.new(a.size,0r)
      order=a.each_index.select{|i|a[i]+b[i]>0}.sort_by{|i|b[i]==0 ? [0,0] : [1,-a[i]/b[i]]}
      order.each do |i|
        da=loss_a*a[i];db=loss_b*b[i]
        f=[1r,(x-y)/(da+db)].min
        policy[i]=f;x-=f*da;y+=f*db
        break if x==y
      end
      {risk:[x,y].max,world_a:x,world_b:y,policy:policy}
    end
    def audit
      p=7r/160;base=R::C.independent([7r/200]*5);vs=R::B.vertices(p,p*p,p*p)
      h=40;r=1r/100;j0=R.finite(base,r,h)
      q=vs.min_by{|v|R.finite(v,r,h)};s=vs.max_by{|v|R.finite(v,r,h)}
      a=j0-R.finite(q,r,h);b=R.finite(s,r,h)-j0
      events={'no_switch'=>[0],'any_switch'=>[1,2,3,4,5],'two_or_more'=>[2,3,4,5],'three_or_more'=>[3,4,5],'all_five'=>[5]}
      {synthetic_only:true,horizon:h,recovery:r.to_f,baseline:j0.to_f,low:R.finite(q,r,h).to_f,high:R.finite(s,r,h).to_f,loss_a:a.to_f,loss_b:b.to_f,low_law:q.map(&:to_s),high_law:s.map(&:to_s),no_data:solve([1r],[1r],a,b)[:risk].to_f,
       events:events.to_h do |name,idx|
         pa=idx.sum{|i|q[i]};pb=idx.sum{|i|s[i]}
         [name,{p_low:pa.to_f,p_high:pb.to_f,risks:[1,10,50,100,500].to_h{|n|[n,solve(binomial(pa,n),binomial(pb,n),a,b)[:risk].to_f]}}]
       end}
    end
  end
end
puts JSON.pretty_generate(RithmT37::Regret.audit) if $PROGRAM_NAME==__FILE__
