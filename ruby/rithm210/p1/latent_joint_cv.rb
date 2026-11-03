# frozen_string_literal: true
require 'csv'
require 'json'
module Rithm210LatentCV
  module_function
  DELTAS=[0.0,0.15,0.30,0.45,0.60,0.90].freeze
  def key(r)=[r['trt'].to_i,r['Informed'].to_i,r['RouteA'].to_i,r['Cost'].to_f]
  def poisson_binomial(ps)
    ps.reduce([1.0]) do |a,p|
      b=Array.new(a.size+1,0.0)
      a.each_with_index{|v,i| b[i]+=v*(1.0-p);b[i+1]+=v*p}
      b
    end
  end
  def logit_shift(p,shift)
    raise ArgumentError,'probability' unless p>0 && p<1
    q= Math.log(p/(1-p))+shift
    1.0/(1.0+Math.exp(-q))
  end
  def probs_for(ps,shift)
    poisson_binomial(ps.map{|p|logit_shift(p,shift)})
  end
  def joint_and_count(pa,pb,u,d,delta)
    total_joint=0.0;total_count=0.0
    [-delta,delta].each do |z|
      up=probs_for(pb,z);dn=probs_for(pa,z)
      total_joint += 0.5*up.fetch(u)*dn.fetch(d)
      count=0.0
      up.each_with_index{|pu,uu|dn.each_with_index{|pd,dd| count+=pu*pd if uu-dd==u-d}}
      total_count += 0.5*count
    end
    raise 'nonpositive likelihood' if total_joint<=0 || total_count<=0
    [-Math.log(total_joint),-Math.log(total_count)]
  end
  def run(path,deltas:DELTAS)
    groups=Hash.new{|h,k|h[k]=[]}
    CSV.foreach(path,headers:true) do |r|
      s=r['session'].to_i;t=r['trt'].to_i;period=r['Period'].to_i
      next unless t.between?(1,3) && s!=2 && s!=101 && period.between?(1,39)
      groups[[s,r['section'].to_i,r['Group'].to_i,period]]<<r
    end
    sessions=groups.keys.map(&:first).uniq.sort
    raise 'source mismatch' unless groups.size==5616 && sessions.size==24 && groups.values.all?{|a|a.size==6}
    folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    scores=deltas.to_h{|x|[x,{joint:0.0,count:0.0,session:Hash.new{|h,k|h[k]={joint:0.0,count:0.0,n:0}}}]}
    6.times do |fold|
      counts=Hash.new{|h,k|h[k]=[0,0]};base=Hash.new{|h,k|h[k]=[0,0]}
      groups.each do |key,a|
        next if folds.fetch(key[0])==fold
        a.each do |r|
          sw=r['switchWill'].to_i
          raise 'invalid outcome' unless [0,1].include?(sw)
          counts[key(r)][0]+=sw;counts[key(r)][1]+=1
          base[r['RouteA'].to_i][0]+=sw;base[r['RouteA'].to_i][1]+=1
        end
      end
      p=->(r){local=counts.fetch(key(r),[0,0]);global=base.fetch(r['RouteA'].to_i,[0,0]);prior=(global[0]+1.0)/(global[1]+2.0); (local[0]+20.0*prior)/(local[1]+20.0)}
      groups.each do |k,a|
        s=k[0];next unless folds.fetch(s)==fold
        pa=a.select{|r|r['RouteA'].to_i==1}.map(&p)
        pb=a.select{|r|r['RouteA'].to_i==0}.map(&p)
        u=a.sum{|r|r['switchBtoAWill'].to_i}; d=a.sum{|r|r['switchAtoBWill'].to_i}
        deltas.each do |delta|
          j,c=joint_and_count(pa,pb,u,d,delta)
          v=scores.fetch(delta);v[:joint]+=j;v[:count]+=c
          ss=v[:session][s];ss[:joint]+=j;ss[:count]+=c;ss[:n]+=1
        end
      end
    end
    {observations:groups.size,sessions:sessions.size,models:scores.map do |delta,score|
      {delta_logit:delta,joint_logloss:score[:joint]/groups.size,count_logloss:score[:count]/groups.size,
       session_rows:score[:session].sort.map{|s,v|{session:s,n:v[:n],joint:v[:joint]/v[:n],count:v[:count]/v[:n]}}}
    end}
  end
end
puts JSON.pretty_generate(Rithm210LatentCV.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
