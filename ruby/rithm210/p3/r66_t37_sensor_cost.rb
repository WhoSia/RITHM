# frozen_string_literal: true
require_relative 'r66_t37_regret'
module RithmT37
  module SensorCost
    R=Regret
    module_function
    def noisy(p,e)
      raise ArgumentError,'error rate' unless e.between?(0,1r/2)
      e+(1-2*e)*p
    end
    def audit
      z=R.audit
      # Reconstruct exact laws and regrets from the original synthetic model.
      q=z[:low_law].map{|x|Rational(x)};s=z[:high_law].map{|x|Rational(x)}
      r=1r/100;h=40;base=R::R.finite(R::R::C.independent([7r/200]*5),r,h)
      a=base-R::R.finite(q,r,h);b=R::R.finite(s,r,h)-base
      ns=[0,1,10,50,100,500];events={'no_switch'=>[0],'two_or_more'=>[2,3,4,5],'all_five'=>[5]}
      errors=[0r,1r/100,1r/20]
      results=errors.map do |e|
        risks=events.to_h{|name,idx|pa=noisy(idx.sum{|i|q[i]},e);pb=noisy(idx.sum{|i|s[i]},e);[name,ns.map{|n|R.solve(R.binomial(pa,n),R.binomial(pb,n),a,b)[:risk]}]}
        costs=[1r/10000,1r/1000,1r/100].map do |fee|
          name,i=risks.keys.product(ns.each_index.to_a).min_by{|k,j|risks[k][j]+fee*ns[j]}
          {cost_per_sample:fee.to_f,sensor:name,n:ns[i],risk:risks[name][i].to_f,total:(risks[name][i]+fee*ns[i]).to_f}
        end
        {error:e.to_f,risks:risks.transform_values{|v|v.map(&:to_f)},grid_optima:costs}
      end
      {synthetic_only:true,sample_sizes:ns,results:results}
    end
  end
end
puts JSON.pretty_generate(RithmT37::SensorCost.audit) if $PROGRAM_NAME==__FILE__
