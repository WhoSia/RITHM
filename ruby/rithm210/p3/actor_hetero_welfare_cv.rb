# frozen_string_literal: true
# Heldout 6-fold session CV: actor-heterogeneous independence must first beat
# calibrated homogeneous independence before interpreting group-dependence.
# Original participant-level CSV remains on Drive and is SHA-verified at runtime.
require_relative '../p2/online_actor_history'
require_relative 'activity_event_cv'
require 'digest'
require 'json'
module Rithm210ActorHeteroWelfareCV
  module_function
  METRICS=[:zero,:cancel,:gross,:loss].freeze
  def predict(people,probabilities)
    p=Rithm210ActivityEventCV.event_probabilities(people,probabilities)
    {zero:p.fetch(:none),cancel:p.fetch(:cancel),
      gross:probabilities.sum,loss:p.fetch(:next_loss)}
  end
  def observed(people)
    u=people.sum{|r|r['switchBtoAWill'].to_i}
    d=people.sum{|r|r['switchAtoBWill'].to_i}
    raise 'next occupancy mismatch' unless people.first['NumAnext'].to_i==4+u-d
    {zero:u+d==0 ? 1 : 0,cancel:u>0&&u==d ? 1 : 0,
      gross:u+d,loss:3*(u-d)**2}
  end
  def source_records(csv)
    raise 'original SHA mismatch' unless Digest::SHA256.file(csv).hexdigest==Rithm210ActivityEventCV::SHA
    groups=Rithm210OnlineIdentity.source(csv)
    sessions=groups.keys.map(&:first).uniq.sort
    raise '24-session source boundary' unless sessions.size==24
    folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    rows=[]
    6.times do |fold|
      held=sessions.select{|s|folds[s]==fold}
      fitted=Rithm210OnlineIdentity.train(groups,held)
      history=Hash.new{|h,k|h[k]=[0,0]}
      keys=groups.keys.select{|key|held.include?(key[0])}.sort_by{|s,section,g,t|[s,section,t,g]}
      keys.each do |s,section,g,t|
        people=groups.fetch([s,section,g,t])
        base=people.map{|r|Rithm210OnlineIdentity.probability(fitted,r)}
        models={baseline:base}
        [20,80].each do |strength|
          models["online_#{strength}".to_sym]=people.each_with_index.map do |r,i|
            Rithm210OnlineIdentity.online_probability(
              base[i],history[[s,section,r['ID'].to_i]],strength.to_f)
          end
        end
        if people.first['trt'].to_i==3 && people.first['NumA'].to_i==4 && (t<=10 || t>=30)
          actual=observed(people)
          models.each do |model,prob|
            rows<<{session:s,model:model,epoch:t<=10 ? :early : :late,
              observed:actual,predicted:predict(people,prob)}
          end
        end
        people.each do |r|
          h=history[[s,section,r['ID'].to_i]]
          h[0]+=r['switchWill'].to_i
          h[1]+=1
        end
      end
    end
    raise 'Full optimum epoch coverage mismatch' unless rows.size==411*3
    [sessions,rows]
  end
  def summary(rows)
    raise 'zero support' if rows.empty?
    n=rows.size.to_f
    {n:rows.size,
     observed:METRICS.to_h{|k|[k,rows.sum{|r|r[:observed][k]}/n]},
     predicted:METRICS.to_h{|k|[k,rows.sum{|r|r[:predicted][k]}/n]},
     residual:METRICS.to_h{|k|[k,rows.sum{|r|r[:observed][k]-r[:predicted][k]}/n]}}
  end
  def run(csv,draws:20_000,seed:20261105)
    sessions,rows=source_records(csv)
    models=rows.group_by{|r|[r[:model],r[:epoch]]}
    counts=models.to_h{|key,a|[key,summary(a)]}
    rng=Random.new(seed)
    ci={}
    models.each do |key,a|
      by_session=a.group_by{|r|r[:session]}
      intervals=METRICS.to_h{|k|[k,[]]}
      draws.times do
        chosen=Array.new(sessions.size){sessions.fetch(rng.rand(sessions.size))}
        sample=chosen.flat_map{|s|by_session.fetch(s,[])}
        next if sample.empty?
        res=summary(sample)[:residual]
        METRICS.each{|k|intervals[k]<<res[k]}
      end
      ci[key]=intervals.to_h do |k,v|
        x=v.sort
        [k,[x[(x.size*0.025).floor],x[(x.size*0.975).floor]]]
      end
    end
    {original_groups:5616,group_samples:411,session_folds:6,
      bootstrap_draws:draws,seed:seed,
      meaning:'heldout actor training; descriptive selected n4 groups; same source repeatedly studied',
      models:counts.to_h{|k,v|[k.join('_'),v]},
      bootstrap95:ci.to_h{|k,v|[k.join('_'),v]}}
  end
end
puts JSON.pretty_generate(Rithm210ActorHeteroWelfareCV.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
