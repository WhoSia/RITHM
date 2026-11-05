# frozen_string_literal: true
# R20: six-person next-route occupancy and welfare bridge, prior-only actor choices.
# Participant CSV remains offline. Descriptive one-step, NOT autonomous welfare.
require 'csv'
require 'digest'
require 'json'
module Rithm210R20GroupBridge
  module_function
  SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'
  def convolve(ps)
    raise ArgumentError,'six probabilities' unless ps.is_a?(Array)&&ps.size==6&&ps.all?{|p|p.is_a?(Numeric)&&p.finite?&&p.between?(0,1)}
    ps.reduce([1.0]) do |dist,p|
      out=Array.new(dist.size+1,0.0)
      dist.each_with_index{|v,n|out[n]+=v*(1-p);out[n+1]+=v*p}
      out
    end
  end
  def cost(n)
    raise ArgumentError,'occupancy 0..6' unless n.is_a?(Integer)&&n.between?(0,6)
    n*n+2*(6-n)**2
  end
  def score(ps,observed_n)
    d=convolve(ps)
    raise ArgumentError,'observed occupancy 0..6' unless observed_n.is_a?(Integer)&&observed_n.between?(0,6)
    {logloss:-Math.log([d[observed_n],Float::MIN].max),
     brier:d.each_with_index.sum{|p,n|(p-(n==observed_n ? 1 : 0))**2},
     predicted_cost:d.each_with_index.sum{|p,n|p*cost(n)},
     observed_cost:cost(observed_n),
     variance:d.each_with_index.sum{|p,n|p*n*n}-ps.sum**2,
     occupancy_mean:ps.sum}
  end
  def summary(rows)
    raise ArgumentError,'empty summary' if rows.empty?
    keys=[:logloss,:brier,:predicted_cost,:observed_cost,:variance,:occupancy_mean]
    {groups:rows.size,**keys.to_h{|k|[k,rows.sum{|r|r.fetch(k)}/rows.size.to_f]},
     cost_bias:rows.sum{|r|r[:predicted_cost]-r[:observed_cost]}/rows.size.to_f,
     cost_abs_error:rows.sum{|r|(r[:predicted_cost]-r[:observed_cost]).abs}/rows.size.to_f}
  end
  def run(path,qmax:2,lapse:0.02)
    require_relative 'r19_ssm_exact'
    require_relative 'r19_persistent_q_filter'
    raise 'original CSV SHA mismatch' unless Digest::SHA256.file(path).hexdigest==SHA
    raise ArgumentError,'qmax 1..9' unless qmax.is_a?(Integer)&&qmax.between?(1,9)
    raise ArgumentError,'lapse' unless lapse.is_a?(Numeric)&&lapse.finite?&&lapse.between?(0,1)
    rows=Hash.new{|h,k|h[k]=[]}
    CSV.foreach(path,headers:true) do |r|
      s=r.fetch('session').to_i;t=r.fetch('Period').to_i
      next if [2,101].include?(s)||!r.fetch('trt').to_i.between?(1,3)||!t.between?(1,40)
      rows[[s,r.fetch('section').to_i,t,r.fetch('Group').to_i]]<<r
    end
    raise 'expected 5760 six-player groups' unless rows.size==5760&&rows.values.all?{|a|a.size==6}
    history={};filters={};scored=[]
    rows.keys.sort.each do |s,section,t,group|
      people=rows.fetch([s,section,t,group]).sort_by{|r|r.fetch('ID').to_i}
      ids=people.map{|r|r.fetch('ID').to_i}
      raise 'duplicate actors' unless ids.uniq.size==6
      trt=people.first.fetch('trt').to_i
      raise 'mixed group treatment' unless people.all?{|r|r.fetch('trt').to_i==trt}
      n=people.sum{|r|r.fetch('RouteA').to_i}
      raise 'NumA mismatch' unless people.all?{|r|r.fetch('NumA').to_i==n}
      probabilities={ssm_uniform:[],ssm_persistent:[],own_route_frequency:[],online_actor_markov:[]}
      states=[]
      people.each do |r|
        key=[s,section,r.fetch('ID').to_i]
        h=history[key]||=Rithm210R19SSMExact.blank_history
        f=filters[key]||=Rithm210R19PersistentQFilter::Filter.new(qmax:qmax,lapse:lapse)
        count=h.fetch(:count,0)
        raise 'actor period discontinuity' unless count==t-1
        inf=r.fetch('Informed')=='1';y=r.fetch('RouteA').to_i
        raise 'nonbinary route' unless [0,1].include?(y)
        persistent=f.predict(history:h,informed:inf)
        probabilities[:ssm_persistent]<<persistent
        probabilities[:ssm_uniform]<<f.last_probabilities.sum/qmax.to_f
        probabilities[:own_route_frequency]<<(h.fetch(:a_count,0)+1).to_f/(count+2)
        if count==0
          probabilities[:online_actor_markov]<<0.5
        else
          prev_a=h.fetch(:previous_a)
          switches=prev_a ? h.fetch(:switch_from_a,0) : h.fetch(:switch_from_b,0)
          trials=prev_a ? h.fetch(:prior_a_count,0) : h.fetch(:prior_b_count,0)
          switch_p=(switches+1).to_f/(trials+5)
          probabilities[:online_actor_markov]<<(prev_a ? 1-switch_p : switch_p)
        end
        states<<[r,h,f,inf,y]
      end
      probabilities.each{|label,ps|scored<<{session:s,treatment:trt,period:t,model:label,**score(ps,n)}}
      # The six prediction probabilities are recorded before ANY outcome from period t.
      states.each do |r,h,f,inf,y|
        f.update(route_a:y==1)
        ten=Rational(r.fetch('profit'))*10
        raise 'unsupported payoff precision' unless ten.denominator==1
        Rithm210R19SSMExact.append(history:h,route_a:y==1,informed:inf,
          payoff_tenths:ten.to_i,num_a:inf ? n : nil)
        if h.key?(:previous_a)
          prior=h.fetch(:previous_a)
          trial=prior ? :prior_a_count : :prior_b_count
          switched=prior ? :switch_from_a : :switch_from_b
          h[trial]=h.fetch(trial,0)+1
          h[switched]=h.fetch(switched,0)+1 if prior != (y==1)
        end
        h[:previous_a]=(y==1)
        h[:count]=t;h[:a_count]=h.fetch(:a_count,0)+y
      end
    end
    raise 'score size mismatch' unless scored.size==5760*4
    by=scored.group_by{|r|[r[:treatment],r[:model]]}
    {sessions:scored.map{|r|r[:session]}.uniq.size,groups:rows.size,qmax:qmax,lapse:lapse,
     estimand:'One-period six-person occupancy distribution and quadratic expected group cost; independent actor conditional predictions.',
     results:by.sort_by{|key,_|key.map(&:to_s)}.map{|(t,m),a|{treatment:t,model:m,**summary(a)}},
     caveat:'Original SSM q latent fit not fully reconstructed. Historical repeated-source exploratory; no causal or autonomous 40-period result.'}
  end
end
puts JSON.pretty_generate(Rithm210R20GroupBridge.run(ARGV.fetch(0),qmax:Integer(ARGV.fetch(1,'2')))) if __FILE__==$PROGRAM_NAME
