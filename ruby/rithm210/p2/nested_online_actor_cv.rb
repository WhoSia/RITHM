# frozen_string_literal: true
# P2-R5: nested session CV for online actor switch history, no future labels.
require_relative 'online_actor_history'
require 'json'

module Rithm210NestedOnlineHistory
  module_function
  STRENGTHS=[5.0,20.0,80.0].freeze

  def folds(sessions,k)
    sessions.sort.each_with_index.to_h{|s,i|[s,i%k]}
  end

  def evaluate(groups,train_sessions,test_sessions,strengths:STRENGTHS)
    all_sessions=groups.keys.map(&:first).uniq
    excluded=all_sessions.reject{|s|train_sessions.include?(s)}
    fit=Rithm210OnlineIdentity.train(groups,excluded)
    keys=groups.keys.select{|k|test_sessions.include?(k[0])}.sort_by{|s,section,g,t|[s,section,t,g]}
    history=Hash.new{|h,k|h[k]=[0,0]}
    labels=[:baseline]+strengths.map{|s|"within_section_#{s.to_i}".to_sym}
    sums=labels.to_h{|label|[label,{joint:0.0,count:0.0,n:0}]}
    keys.each do |session,section,group,t|
      people=groups.fetch([session,section,group,t])
      base=people.map{|r|Rithm210OnlineIdentity.probability(fit,r)}
      models={baseline:base}
      strengths.each do |strength|
        label="within_section_#{strength.to_i}".to_sym
        models[label]=people.each_with_index.map do |r,i|
          h=history[[session,section,r['ID'].to_i]]
          Rithm210OnlineIdentity.online_probability(base[i],h,strength)
        end
      end
      models.each do |label,probs|
        joint,count,_=Rithm210OnlineIdentity.group_scores(people,probs)
        sums[label][:joint]+=joint
        sums[label][:count]+=count
        sums[label][:n]+=1
      end
      # After scoring period t, record its outcome strictly for future periods.
      people.each do |r|
        h=history[[session,section,r['ID'].to_i]]
        h[0]+=r['switchWill'].to_i
        h[1]+=1
      end
    end
    sums
  end

  def run(path)
    groups=Rithm210OnlineIdentity.source(path)
    sessions=groups.keys.map(&:first).uniq.sort
    raise 'unexpected sessions' unless sessions.size==24
    outer=folds(sessions,6)
    reports=[]
    6.times do |o|
      test=sessions.select{|s|outer[s]==o}
      training=sessions.reject{|s|outer[s]==o}
      raise 'outer overlap' unless test.size==4 && training.size==20
      inner=folds(training,5)
      validation_sums=Hash.new{|h,k|h[k]={joint:0.0,count:0.0,n:0}}
      5.times do |f|
        validation=training.select{|s|inner[s]==f}
        fit_sessions=training.reject{|s|inner[s]==f}
        raise 'inner leak' unless validation.size==4 && fit_sessions.size==16 && (fit_sessions & test).empty?
        evaluate(groups,fit_sessions,validation).each do |label,r|
          accumulator=validation_sums[label]
          [:joint,:count,:n].each{|metric|accumulator[metric]+=r[metric]}
        end
      end
      candidates=STRENGTHS.map{|s|"within_section_#{s.to_i}".to_sym}
      winner_joint=candidates.min_by{|label|[validation_sums[label][:joint]/validation_sums[label][:n],label.to_s]}
      winner_count=candidates.min_by{|label|[validation_sums[label][:count]/validation_sums[label][:n],label.to_s]}
      outer_score=evaluate(groups,training,test)
      reports << {fold:o,n:outer_score[:baseline][:n],
        selected_joint:winner_joint,selected_count:winner_count,
        baseline:outer_score[:baseline],
        joint_selected:outer_score.fetch(winner_joint),
        count_selected:outer_score.fetch(winner_count),
        inner:validation_sums.transform_values{|r|{joint:r[:joint]/r[:n],count:r[:count]/r[:n]}}}
    end
    total=reports.sum{|r|r[:n]}
    raise 'not 5616 group transitions' unless total==5616
    {n:total,
      selected_joint:reports.map{|r|r[:selected_joint]}.tally,
      selected_count:reports.map{|r|r[:selected_count]}.tally,
      joint_baseline:reports.sum{|r|r[:baseline][:joint]}/total,
      joint_selected:reports.sum{|r|r[:joint_selected][:joint]}/total,
      count_baseline:reports.sum{|r|r[:baseline][:count]}/total,
      count_selected:reports.sum{|r|r[:count_selected][:count]}/total,
      folds:reports}
  end
end

puts JSON.pretty_generate(Rithm210NestedOnlineHistory.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
