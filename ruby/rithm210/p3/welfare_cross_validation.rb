# frozen_string_literal: true
require_relative 'welfare_probability'
require 'json'

module Rithm210WelfareCrossValidation
  module_function
  def run(csv)
    groups=Rithm210OnlineIdentity.source(csv)
    sessions=groups.keys.map(&:first).uniq.sort
    raise 'source session count' unless sessions.size==24 && groups.size==5616
    folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    summary=Hash.new{|h,k|h[k]=Hash.new(0.0)}
    session_scores=Hash.new{|h,k|h[k]=Hash.new{|hh,name|hh[name]=Hash.new(0.0)}}
    6.times do |fold|
      held=sessions.select{|s|folds[s]==fold}
      fitted=Rithm210OnlineIdentity.train(groups,held)
      history=Hash.new{|h,k|h[k]=[0,0]}
      keys=groups.keys.select{|key|held.include?(key[0])}.
        sort_by{|s,sec,g,t|[s,sec,t,g]}
      keys.each do |s,sec,g,t|
        people=groups.fetch([s,sec,g,t])
        n=people.first['NumA'].to_i
        next_a=people.first['NumAnext'].to_i
        raise 'next occupancy mismatch' unless next_a==n+
          people.sum{|r|r['switchBtoAWill'].to_i}-
          people.sum{|r|r['switchAtoBWill'].to_i}
        observed=Rithm210ExperimentalWelfare.excess(next_a)
        base=people.map{|r|Rithm210OnlineIdentity.probability(fitted,r)}
        variants={baseline:base}
        [20,80].each do |strength|
          variants["online_#{strength}".to_sym]=people.each_with_index.map do |r,i|
            past=history[[s,sec,r['ID'].to_i]]
            Rithm210OnlineIdentity.online_probability(base[i],past,strength.to_f)
          end
        end
        variants.each do |name,prob|
          score=Rithm210WelfareProbability.scoring(
            Rithm210WelfareProbability.law(people,prob,n),observed)
          score.each do |key,value|
            summary[name][key]+=value
            session_scores[s][name][key]+=value
          end
          summary[name][:n]+=1
          session_scores[s][name][:n]+=1
        end
        # Period-t observations update only after evaluating all period-t forecasts.
        people.each do |r|
          h=history[[s,sec,r['ID'].to_i]]
          h[0]+=r['switchWill'].to_i;h[1]+=1
        end
      end
    end
    raise 'incomplete evaluation' unless summary.values.all?{|h|h[:n]==5616}
    normal=->(a){a.to_h{|k,v|[k,k==:n ? v.to_i : v/a[:n]]}}
    {n:5616,models:summary.transform_values(&normal),
      by_session:session_scores.transform_values{|a|a.transform_values(&normal)}}
  end
end
puts JSON.pretty_generate(Rithm210WelfareCrossValidation.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
