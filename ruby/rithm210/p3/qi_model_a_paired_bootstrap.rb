# frozen_string_literal: true
# P3-R16D: paired out-of-session Qi Model A vs epoch20 independent actor forecasts.
# One dataset, fixed predictions, session-level conditional uncertainty. No private rows emitted.
require_relative 'qi_model_a_transfer'
require_relative 'all_state_epoch_cv'
require 'json'
module Rithm210QiModelAPairedBootstrap
  module_function
  Q=Rithm210QiModelATransfer
  M=Rithm210AllStateEpochCV
  E=Rithm210EpochIndependentWelfare
  O=Rithm210OnlineIdentity
  def source_blocks(csv)
    raise 'source SHA mismatch' unless Digest::SHA256.file(csv).hexdigest==E::SHA
    groups=O.source(csv)
    sessions=groups.keys.map(&:first).uniq.sort
    raise '24 sessions required' unless sessions.size==24
    fold=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    blocks=Hash.new{|h,k|h[k]=[]}
    6.times do |f|
      held=sessions.select{|s|fold[s]==f}
      qi=Q.fit(Q.counts(groups,held))[:params]
      markov=O.train(groups,held)
      epoch=E.train_epoch(groups,held)
      groups.each do |(s,section,g,t),people|
        next unless held.include?(s) && people.first['trt'].to_i==3
        qprobs=people.map{|r|Q.switch_probability(qi,r['RouteA'].to_i,r['NumA'].to_i)}
        base=people.map{|r|O.probability(markov,r)}
        eprobs=people.each_with_index.map{|r,i|E.probability(base[i],epoch,r,t)}
        q=M.group_score(people,qprobs)
        e=M.group_score(people,eprobs)
        blocks[s]<<{epoch:E.epoch(t),joint_delta:q[:joint]-e[:joint],
                    count_delta:q[:count]-e[:count]}
      end
    end
    raise '1872 scored groups required' unless blocks.values.sum(&:size)==1872
    [sessions,blocks]
  end
  def bootstrap(sessions,blocks,draws:20_000,seed:20261105)
    raise ArgumentError,'positive draws and nonempty sessions required' unless draws.positive? && !sessions.empty?
    rng=Random.new(seed)
    conditions={all:->(r){true},early:->(r){r[:epoch]==:early},
                late:->(r){r[:epoch]==:late}}
    conditions.to_h do |name,predicate|
      cells=sessions.map do |s|
        rows=blocks.fetch(s,[]).select(&predicate)
        [rows.size,rows.sum{|r|r.fetch(:joint_delta)},rows.sum{|r|r.fetch(:count_delta)}]
      end
      n=cells.sum{|row|row[0]}
      raise 'empty contrast' if n==0
      point=cells.sum{|row|row[1]}/n.to_f
      a=[]
      draws.times do
        sample=Array.new(sessions.size){cells.fetch(rng.rand(sessions.size))}
        count=sample.sum{|x|x[0]}
        next if count==0
        a<<sample.sum{|x|x[1]}/count.to_f
      end
      a.sort!
      [name,{n:n,qi_minus_epoch_joint_logloss:point,
             conditional_session_bootstrap95:[a.fetch((a.size*0.025).floor),
                                                a.fetch((a.size*0.975).floor)],
             valid_draws:a.size}]
    end
  end
  def run(path)
    sessions,blocks=source_blocks(path)
    {sessions:sessions.size,results:bootstrap(sessions,blocks),
     warning:'Qi Part I Model A formula fitted to DIFFERENT experiment; no nested tuning, repeated within-source exploration; fixed-CV-prediction block bootstrap.'}
  end
end
puts JSON.pretty_generate(Rithm210QiModelAPairedBootstrap.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
