# frozen_string_literal: true
require 'json'
module RithmThreeAgentInspection
  module_function
  INITIAL=[0,0,1].freeze
  PLANS=([[false,0,0],[false,1,1]]+[0,1].product([0,1]).map{|a,b|[true,a,b]}).freeze
  def result(plans,z,k,q)
    routes=plans.map{|plan|plan[z+1]};a=routes.count(0);b=3-a
    losses=3.times.map{|i|(routes[i]==0 ? a+z : b)+(routes[i]!=INITIAL[i] ? k : 0)+(plans[i][0] ? q : 0)}
    [losses,losses.sum,routes]
  end
  def expected(plans,k:,q:,p:)
    low=result(plans,0,k,q);high=result(plans,1,k,q)
    [3.times.map{|i|(1-p)*low[0][i]+p*high[0][i]},(1-p)*low[1]+p*high[1]]
  end
  def audit(k:Rational(3,4),q:Rational(1,16),p:Rational(1,2),depth:6)
    raise ArgumentError unless k>=0&&q>=0&&p.between?(0,1)&&depth.between?(1,6)
    equilibria=[];approx=[];profiles=0
    PLANS.repeated_permutation(3) do |ps|
      profiles+=1
      current=expected(ps,k:k,q:q,p:p)
      deviations=3.times.map do |i|
        alternatives=PLANS.each_with_index.map{|alt,j|[alt,j]}.first(depth)
        alternatives.map do |alt,j|
          rival=ps.dup;rival[i]=alt
          [expected(rival,k:k,q:q,p:p)[0][i]-current[0][i],j]
        end
      end
      eps=deviations.flatten(1).map{|x|x[0]}.min
      row={'plans'=>ps,'individual'=>current[0],'social'=>current[1]}
      equilibria<<row if 3.times.all?{|i|PLANS.all?{|alt|
        rival=ps.dup;rival[i]=alt
        expected(rival,k:k,q:q,p:p)[0][i]>=current[0][i]}}
      approx<<row if eps>=0
    end
    {'profiles'=>profiles,'pure_equilibria'=>equilibria,'depth_limited_stable'=>approx.size,
     'depth'=>depth,'mixed_equilibrium'=>'NOT CHECKED','human_validated'=>false}
  end
end
if $PROGRAM_NAME==__FILE__
 r=RithmThreeAgentInspection.audit
 puts JSON.pretty_generate(r)
end
