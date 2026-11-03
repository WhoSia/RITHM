# frozen_string_literal: true
require_relative 'actor_calibration'
module Rithm210EpochConditionedModel
  module_function
  def epoch(period)
    Rithm210ActorCalibration.epoch(period)
  end
  def train(groups,folds,fold)
    base=Rithm210ResidualNegativeControl.fit(groups,folds,fold)
    epoch_counts=Hash.new{|h,k|h[k]=[0,0]}
    groups.each do |key,people|
      next if folds.fetch(key[0])==fold
      e=epoch(key[3])
      people.each do |r|
        x=[*Rithm210ResidualNegativeControl.key(r),e]
        tally=epoch_counts[x]
        tally[0]+=r.fetch('switchWill').to_i
        tally[1]+=1
      end
    end
    [base,epoch_counts]
  end
  def probability(model,r,period,conditional:,alpha:20.0)
    base,by_epoch=model
    prior=Rithm210ResidualNegativeControl.probability(base,r)
    return prior unless conditional
    k=[*Rithm210ResidualNegativeControl.key(r),epoch(period)]
    observed=by_epoch.fetch(k,[0,0])
    (observed[0]+alpha*prior)/(observed[1]+alpha)
  end
  def convolve(ps)
    ps.reduce([1.0]) do |q,p|
      out=Array.new(q.length+1,0.0)
      q.each_with_index{|v,i|out[i]+=v*(1-p);out[i+1]+=v*p}
      out
    end
  end
  def joint_and_count(pa,pb,u,d)
    up=convolve(pb);dn=convolve(pa)
    joint=up.fetch(u)*dn.fetch(d)
    total=0.0
    up.each_with_index{|p,i|dn.each_with_index{|q,j|total+=p*q if i-j==u-d}}
    raise 'zero score' unless joint>0 && total>0
    [-Math.log(joint),-Math.log(total)]
  end
  def run(path)
    groups=Rithm210ResidualNegativeControl.read_groups(path)
    sessions=groups.keys.map(&:first).uniq.sort
    folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    result=Hash.new{|h,k|h[k]=[]}
    6.times do |fold|
      fit=train(groups,folds,fold)
      groups.each do |(s,sec,g,t),people|
        next unless folds[s]==fold
        u=people.sum{|r|r['switchBtoAWill'].to_i};d=people.sum{|r|r['switchAtoBWill'].to_i}
        [false,true].each do |conditional|
          get=->(r){probability(fit,r,t,conditional:conditional)}
          pa=people.select{|r|r['RouteA'].to_i==1}.map(&get)
          pb=people.select{|r|r['RouteA'].to_i==0}.map(&get)
          joint,count=joint_and_count(pa,pb,u,d)
          ru=u-pb.sum;rd=d-pa.sum
          result[conditional ? :epoch : :baseline] << {session:s,joint:joint,count:count,cross:ru*rd}
        end
      end
    end
    out=result.to_h{|k,rows|[k,[:joint,:count,:cross].to_h{|metric|[metric,rows.sum{|r|r[metric]}/rows.size.to_f]}]}
    diff=[:joint,:count,:cross].to_h{|metric|[metric,out[:epoch][metric]-out[:baseline][metric]]}
    {n:5616,sessions:24,baseline:out[:baseline],epoch:out[:epoch],delta:diff,
      session_delta:sessions.map do |s|
        a=result[:baseline].select{|x|x[:session]==s};b=result[:epoch].select{|x|x[:session]==s}
        {session:s,n:a.length,**[:joint,:count,:cross].to_h{|metric|[metric,(b.sum{|x|x[metric]}-a.sum{|x|x[metric]})/a.length.to_f]}}
      end}
  end
end
puts JSON.pretty_generate(Rithm210EpochConditionedModel.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
