# frozen_string_literal: true
# R16E: same heldout group events, fit Qi A/B/C on training sessions only,
# then paired whole-session resample fixed forecasts. Private rows never printed.
require_relative 'qi_abc_transfer'
require 'json'
module Rithm210QiABCSessionContrast
  module_function
  Q=Rithm210QiABCTest
  A=Rithm210QiModelATransfer
  O=Rithm210OnlineIdentity
  E=Rithm210EpochIndependentWelfare
  M=Rithm210AllStateEpochCV
  def scores_by_session(path)
    raise 'SHA mismatch' unless Digest::SHA256.file(path).hexdigest==E::SHA
    groups=O.source(path)
    sessions=groups.keys.map(&:first).uniq.sort
    raise '24 sessions required' unless sessions.size==24
    folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    by=Hash.new{|h,k|h[k]=[]}
    6.times do |f|
      held=sessions.select{|s|folds[s]==f}
      cells=A.counts(groups,held)
      fits=Q::VARIANTS.to_h{|kind|[kind,Q.fit(kind,cells)[:params]]}
      groups.each do |(s,sec,g,t),people|
        next unless held.include?(s) && people.first['trt'].to_i==3
        losses=Q::VARIANTS.to_h do |kind|
          ps=people.map{|r|Q.probability(kind,fits.fetch(kind),r['RouteA'].to_i,r['NumA'].to_i)}
          [kind,M.group_score(people,ps)[:joint]]
        end
        by[s]<<{epoch:E.epoch(t),**losses}
      end
    end
    raise '1872 heldout groups' unless by.values.sum(&:size)==1872
    [sessions,by]
  end
  def bootstrap(sessions,by,draws:20_000,seed:20261105)
    raise ArgumentError,'positive draws and sessions required' unless draws.positive? && !sessions.empty?
    rng=Random.new(seed)
    contrasts={a_minus_c:[:a,:c],b_minus_c:[:b,:c],b_minus_a:[:b,:a]}
    scopes={all:->(r){true},early:->(r){r[:epoch]==:early},late:->(r){r[:epoch]==:late}}
    scopes.to_h do |label,predicate|
      cells=sessions.map do |s|
        rows=by.fetch(s,[]).select(&predicate)
        [rows.size,contrasts.to_h{|name,(x,y)|[name,rows.sum{|r|r.fetch(x)-r.fetch(y)}]}]
      end
      size=cells.sum(&:first)
      raise 'empty scope' unless size>0
      pairs=contrasts.to_h do |name,axes|
        point=cells.sum{|n,vals|vals.fetch(name)}/size.to_f
        replicates=[]
        draws.times do
          drawn=Array.new(sessions.size){cells.fetch(rng.rand(sessions.size))}
          denominator=drawn.sum(&:first)
          next if denominator==0
          replicates<<drawn.sum{|n,vals|vals.fetch(name)}/denominator.to_f
        end
        replicates.sort!
        [name,{delta:point,ci95:[replicates.fetch((replicates.size*0.025).floor),
                                replicates.fetch((replicates.size*0.975).floor)],
               valid_draws:replicates.size}]
      end
      [label,{n:size,contrasts:pairs}]
    end
  end
  def run(path)
    sessions,by=scores_by_session(path)
    {sessions:sessions.length,draws:20_000,results:bootstrap(sessions,by),
     limitation:'original-source repeated model exploration; fixed 6fold fitted forecasts, no refit bootstrap; not a causal or new-study result'}
  end
end
puts JSON.pretty_generate(Rithm210QiABCSessionContrast.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
