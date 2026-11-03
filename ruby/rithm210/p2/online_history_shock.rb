# frozen_string_literal: true
# P2-R5: fixed gamma shared-shock mixture AFTER prior-only online actor history.
require_relative 'online_actor_history'
require 'json'

module Rithm210OnlineHistoryShock
  module_function

  def shifted(p,delta)
    x=Math.log(p/(1.0-p))+delta
    1.0/(1.0+Math.exp(-x))
  end

  def group_scores(people,probabilities,gamma)
    up=[];down=[];u=0;d=0
    people.each_with_index do |r,i|
      if r['RouteA'].to_i==1
        down << probabilities[i]
        d += r['switchAtoBWill'].to_i
      else
        up << probabilities[i]
        u += r['switchBtoAWill'].to_i
      end
    end
    joint=0.0
    count=0.0
    [-gamma,gamma].each do |z|
      pu=Rithm210OnlineIdentity.convolve(up.map{|p|shifted(p,z)})
      pd=Rithm210OnlineIdentity.convolve(down.map{|p|shifted(p,z)})
      joint+=pu.fetch(u)*pd.fetch(d)/2.0
      pu.each_with_index{|v,i|pd.each_with_index{|w,j|count+=v*w/2.0 if i-j==u-d}}
    end
    raise 'nonpositive mixture probability' unless joint>0 && count>0
    [-Math.log(joint),-Math.log(count)]
  end

  def run(path,gammas:[0.0,0.15,0.30,0.45],strength:20.0)
    groups=Rithm210OnlineIdentity.source(path)
    sessions=groups.keys.map(&:first).uniq.sort
    folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    scores=gammas.to_h do |gamma|
      [gamma,{joint:0.0,count:0.0,n:0,
        by_session:Hash.new{|h,k|h[k]={joint:0.0,count:0.0,n:0}}}]
    end
    6.times do |fold|
      held=sessions.select{|s|folds[s]==fold}
      fit=Rithm210OnlineIdentity.train(groups,held)
      history=Hash.new{|h,k|h[k]=[0,0]}
      keys=groups.keys.select{|k|held.include?(k[0])}.sort_by{|s,section,g,t|[s,section,t,g]}
      keys.each do |session,section,group,period|
        people=groups.fetch([session,section,group,period])
        base=people.map{|r|Rithm210OnlineIdentity.probability(fit,r)}
        online=people.each_with_index.map do |r,i|
          h=history[[session,section,r['ID'].to_i]]
          Rithm210OnlineIdentity.online_probability(base[i],h,strength)
        end
        gammas.each do |gamma|
          joint,count=group_scores(people,online,gamma)
          score=scores.fetch(gamma)
          score[:joint]+=joint;score[:count]+=count;score[:n]+=1
          row=score[:by_session][session]
          row[:joint]+=joint;row[:count]+=count;row[:n]+=1
        end
        people.each do |r|
          h=history[[session,section,r['ID'].to_i]]
          h[0]+=r['switchWill'].to_i;h[1]+=1
        end
      end
    end
    {strength:strength,sessions:24,groups:5616,
      models:scores.to_h do |gamma,result|
        [gamma,{joint:result[:joint]/result[:n],count:result[:count]/result[:n],
          by_session:result[:by_session].transform_values{|r|{n:r[:n],
            joint:r[:joint]/r[:n],count:r[:count]/r[:n]}}}]
      end}
  end
end

puts JSON.pretty_generate(Rithm210OnlineHistoryShock.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
