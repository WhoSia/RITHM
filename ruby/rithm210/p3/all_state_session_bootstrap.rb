# frozen_string_literal: true
# R16B paired session-block uncertainty of epoch-minus-Markov predictions.
# Refit NOT performed inside resamples; exploratory and source-dependent only.
require_relative 'all_state_epoch_cv'
require 'json'
module Rithm210AllStateSessionBootstrap
  module_function
  E=Rithm210EpochIndependentWelfare
  O=Rithm210OnlineIdentity
  M=Rithm210AllStateEpochCV
  METRICS=[:joint,:count,:error,:gross_pred].freeze
  def source_deltas(csv)
    raise 'SHA mismatch' unless Digest::SHA256.file(csv).hexdigest==E::SHA
    groups=O.source(csv);sessions=groups.keys.map(&:first).uniq.sort
    raise '24 sessions required' unless sessions.size==24
    fold=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    by_session=Hash.new{|h,k|h[k]=[]}
    6.times do |f|
      held=sessions.select{|s|fold[s]==f}
      fitted=O.train(groups,held)
      tally=E.train_epoch(groups,held)
      groups.each do |(s,section,group,t),people|
        next unless fold[s]==f
        base=people.map{|r|O.probability(fitted,r)}
        calibrated=people.each_with_index.map{|r,i|E.probability(base[i],tally,r,t)}
        before=M.group_score(people,base)
        after=M.group_score(people,calibrated)
        by_session[s]<<{trt:people.first['trt'].to_i,epoch:E.epoch(t),
                       metrics:METRICS.to_h{|k|[k,after[k]-before[k]]}}
      end
    end
    raise 'all source groups must be scored once' unless by_session.values.sum(&:size)==5616
    [sessions,by_session]
  end
  def quantile(a,p)
    raise ArgumentError,'nonempty values' if a.empty?
    a.sort.fetch((a.length*p).floor)
  end
  def bootstrap(sessions,blocks,draws:20_000,seed:20261105)
    raise ArgumentError,'positive draws' unless draws.positive?
    rng=Random.new(seed)
    conditioned={all:->(r){true},full_early:->(r){r[:trt]==3 && r[:epoch]==:early},
                 full_late:->(r){r[:trt]==3 && r[:epoch]==:late}}
    conditioned.to_h do |stratum,filter|
      cells=sessions.map do |s|
        a=blocks.fetch(s,[]).select(&filter)
        [a.size,METRICS.to_h{|k|[k,a.sum{|r|r[:metrics][k]}]}]
      end
      total=cells.sum(&:first)
      raise 'empty stratum' unless total>0
      point=METRICS.to_h{|k|[k,cells.sum{|n,sum|sum[k]}/total.to_f]}
      sampled=METRICS.to_h{|k|[k,[]]}
      draws.times do
        selection=Array.new(sessions.length){cells.fetch(rng.rand(sessions.length))}
        count=selection.sum(&:first)
        next if count==0
        METRICS.each{|k|sampled[k]<<selection.sum{|n,sum|sum[k]}/count.to_f}
      end
      [stratum,{n:total,point:point,conditional_session_bootstrap95:sampled.to_h{|k,v|
        [k,[quantile(v,0.025),quantile(v,0.975)]]}}]
    end
  end
  def run(csv)
    sessions,by_session=source_deltas(csv)
    {sessions:sessions.size,selected_groups:5616,draws:20_000,
     strata:bootstrap(sessions,by_session),
     caveat:'Same repeatedly explored original source; trained CV predictions fixed; no nested-tuning or refit uncertainty.'}
  end
end
puts JSON.pretty_generate(Rithm210AllStateSessionBootstrap.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
