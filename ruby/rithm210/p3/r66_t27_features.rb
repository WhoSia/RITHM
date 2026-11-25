# frozen_string_literal: true
require_relative 'r66_t26_forecast'
module RithmT27
  module Features
    F=RithmT26::Forecast
    BASE=[1,10,40,80,80,32].map{|v|v/243.0}.freeze
    MODES=[:route,:observation,:history,:both,:duration,:frailty,:belief,:behavior,:behavior_belief].freeze
    PARENTS=[nil,0,0,1,1,1,1,3,7].freeze
    module_function
    def posterior(prior,mask,rho)
      w=prior.each_with_index.map{|v,k| (mask & (1<<k))==0 ? 0.0 : v}
      z=w.sum;raise 'incompatible observation' unless z>0
      w.each_with_index.map{|v,k|rho*v/z+(1-rho)*BASE[k]}
    end
    def records(rows,periods:40,rho:0.5)
      raise ArgumentError,'rho' unless rho>=0 && rho<1
      rows.group_by{|r|r.values_at('session','Group','trt','ID')}.flat_map do |id,rs|
        rs=rs.sort_by{|r|Integer(r['Period'])}
        raise 'incomplete trajectory' unless rs.map{|r|Integer(r['Period'])}==(1..periods).to_a
        prior=BASE;duration=0;switches=0;previous=nil
        rs.each_with_index.filter_map do |r,i|
          a=Integer(r['RouteA']);past=previous ? (a-Integer(previous['RouteA'])).abs : 0
          keys=F.keys(r,previous||r);obs=keys[1].last
          mask=Integer(r['Informed'])==1 ? 1<<obs : obs
          prior=posterior(prior,mask,rho)
          duration=past==1 ? 1 : duration+1
          # Past propensity excludes the most recent switch; all inputs precede target.
          propensity=(4*(switches+1))/(i+1)
          propensity=[3,propensity].min
          switches+=past;previous=r
          next if i==0 || i==periods-1
          d=case duration;when 1 then 0;when 2 then 1;when 3..4 then 2;when 5..8 then 3;else 4;end
          gain=prior.each_with_index.sum{|v,k|v*(3*k-11)}*(a==1 ? 1 : -1)
          b=gain.floor;obs_key=keys[1];both=keys[3]
          ks=keys+[obs_key+[d],obs_key+[propensity],obs_key+[b],both+[d,propensity],both+[d,propensity,b]]
          [id[0],ks,(a-Integer(rs[i+1]['RouteA'])).abs]
        end
      end
    end
  end
end
