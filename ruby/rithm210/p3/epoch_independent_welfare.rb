# frozen_string_literal: true
# P3-R14: train-session-only epoch strata, fixed alpha=20; actor independence.
# Author-approved source stays in Drive; public results are aggregates only.
require_relative '../p2/online_actor_history'
require_relative 'group_residual_welfare'
require 'digest'
require 'json'
module Rithm210EpochIndependentWelfare
  module_function
  SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'
  def epoch(t)
    return :early if t<=10
    return :late if t>=30
    :middle
  end
  def train_epoch(groups,held)
    tally=Hash.new{|h,k|h[k]=[0,0]}
    groups.each do |(s,sec,g,t),people|
      next if held.include?(s)
      people.each do |r|
        k=[*Rithm210OnlineIdentity.actor_key(r),epoch(t)]
        a=tally[k];a[0]+=r['switchWill'].to_i;a[1]+=1
      end
    end
    tally
  end
  def probability(base,tally,r,t,alpha:20.0)
    raise ArgumentError,'alpha must be positive' unless alpha.positive?
    a=tally.fetch([*Rithm210OnlineIdentity.actor_key(r),epoch(t)],[0,0])
    (a[0]+alpha*base)/(a[1]+alpha)
  end
  def source_rows(path)
    raise 'SHA mismatch' unless Digest::SHA256.file(path).hexdigest==SHA
    groups=Rithm210OnlineIdentity.source(path)
    sessions=groups.keys.map(&:first).uniq.sort
    raise '24 sessions required' unless sessions.size==24
    folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    rows=[]
    6.times do |f|
      held=sessions.select{|s|folds[s]==f}
      basefit=Rithm210OnlineIdentity.train(groups,held)
      tally=train_epoch(groups,held)
      keys=groups.keys.select{|k|held.include?(k[0])}.sort_by{|s,sec,g,t|[s,sec,t,g]}
      keys.each do |s,sec,g,t|
        people=groups.fetch([s,sec,g,t])
        next unless people.first['trt'].to_i==3 && people.first['NumA'].to_i==4 && (t<=10||t>=30)
        base=people.map{|r|Rithm210OnlineIdentity.probability(basefit,r)}
        epochp=people.each_with_index.map{|r,i|probability(base[i],tally,r,t)}
        routes=people.map{|r|r['RouteA'].to_i}
        actual=people.map{|r|r['switchWill'].to_i}
        [[ :baseline,base],[:epoch20,epochp]].each do |model,ps|
          metrics=Rithm210GroupResidualWelfare.analyze(routes,actual,ps)
          rows<<{session:s,epoch:epoch(t),model:model,metrics:metrics,
                 individual:actual.each_with_index.map{|y,i|{route:routes[i],y:y,p:ps[i]}}}
        end
      end
    end
    raise '411*2 target groups required' unless rows.length==822
    [sessions,rows]
  end
  def summarize(rows)
    by=rows.group_by{|r|[r[:model],r[:epoch]]}
    by.to_h do |k,a|
      results=Rithm210GroupResidualWelfare.aggregate(a.map{|r|r[:metrics]})
      actors=a.flat_map{|r|r[:individual]}
      results[:individual_brier]=actors.sum{|r|(r[:y]-r[:p])**2}/actors.size.to_f
      results[:individual_bias]=actors.sum{|r|r[:y]-r[:p]}/actors.size.to_f
      results[:individual_logloss]=actors.sum{|r|-Math.log([r[:y]==1 ? r[:p] : 1-r[:p],1e-300].max)}/actors.size.to_f
      [k.join('_'),results]
    end
  end
  def run(path)
    sessions,rows=source_rows(path)
    {sessions:sessions.length,selected_groups:rows.size/2,models:summarize(rows)}
  end
end
puts JSON.pretty_generate(Rithm210EpochIndependentWelfare.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
