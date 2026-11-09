# frozen_string_literal: true
# RITHM R23: group-level prior-only memory x inertia heldout comparison.
# Original private participant CSV required only at invocation; never upload it.
require 'csv'
require 'digest'
require 'json'
require_relative 'r20_group_bridge'
require_relative 'r23_actor_memory'
module Rithm210R23GroupMemoryCV
  module_function
  A=Rithm210R23ActorMemory
  SOURCE_SHA=Rithm210R20GroupBridge::SHA
  def source(path)
    raise 'original CSV SHA mismatch' unless Digest::SHA256.file(path).hexdigest==SOURCE_SHA
    groups=Hash.new{|h,k|h[k]=[]}
    CSV.foreach(path,headers:true) do |r|
      s=r.fetch('session').to_i;t=r.fetch('Period').to_i;trt=r.fetch('trt').to_i
      next if [2,101].include?(s)||!trt.between?(1,3)||!t.between?(1,40)
      groups[[s,r.fetch('section').to_i,t,r.fetch('Group').to_i]]<<r
    end
    raise 'expected 5760 complete 6-person groups' unless groups.size==5760&&groups.values.all?{|v|v.size==6}
    groups
  end
  def evaluate(groups,configs:A.candidates)
    raise ArgumentError,'nonempty unique configs' unless configs.is_a?(Array)&&!configs.empty?&&configs.uniq==configs
    history={};records=Hash.new{|h,k|h[k]=[0.0,0.0,0.0,0.0,0]}
    groups.keys.sort.each do |s,section,t,group|
      people=groups.fetch([s,section,t,group]).sort_by{|r|r.fetch('ID').to_i}
      ids=people.map{|r|r.fetch('ID').to_i}
      raise 'duplicate actor' unless ids.uniq.size==6
      trt=people.first.fetch('trt').to_i
      raise 'mixed treatment' unless people.all?{|r|r.fetch('trt').to_i==trt}
      choices=people.map{|r|Integer(r.fetch('RouteA'))}
      raise 'invalid choice' unless choices.all?{|v|[0,1].include?(v)}
      n=choices.sum
      raise 'group occupancy mismatch' unless people.all?{|r|r.fetch('NumA').to_i==n}
      actors=ids.map{|id|history[[s,section,id]]||=A::State.new}
      raise 'history out of order' unless actors.all?{|a|a.periods==t-1}
      # Every model forecast is computed before any period-t state update.
      configs.each do |config|
        probabilities=actors.map{|a|A.forecast(a,config)}
        score=Rithm210R20GroupBridge.score(probabilities,n)
        row=records[[s,trt,A.label(config)]]
        row[0]+=score.fetch(:logloss)
        row[1]+=score.fetch(:brier)
        error=score.fetch(:predicted_cost)-score.fetch(:observed_cost)
        row[2]+=error.abs;row[3]+=error;row[4]+=1
      end
      actors.zip(choices).each{|a,choice|a.update(choice)}
    end
    records.sort_by{|(s,t,m),_|[s,t,m]}.map do |(s,t,m),values|
      n=values.fetch(4)
      {session:s,treatment:t,model:m,groups:n,
       logloss:values[0]/n,brier:values[1]/n,
       cost_abs_error:values[2]/n,cost_bias:values[3]/n}
    end
  end
  def cross_validate(rows,draws:4000,seed:20261109)
    raise ArgumentError,'positive draws' unless draws.is_a?(Integer)&&draws>0
    sessions=rows.map{|r|r.fetch(:session)}.uniq.sort
    raise 'expected 24 independent sessions' unless sessions.size==24
    names=rows.map{|r|r.fetch(:model)}.uniq.sort
    baseline=A.label([1.0,5.0,0.0])
    raise 'frequency baseline missing' unless names.include?(baseline)
    index=rows.to_h{|r|[[r.fetch(:session),r.fetch(:treatment),r.fetch(:model)],r]}
    raise 'duplicate group scoring cell' unless index.size==rows.size
    foldmap=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    output=[];fold_choices=[]
    6.times do |fold|
      heldout=sessions.select{|s|foldmap[s]==fold}
      training=sessions-heldout
      (1..3).each do |trt|
        winner=names.min_by do |name|
          train_loss=training.sum{|s|index.fetch([s,trt,name]).fetch(:logloss)}/training.size.to_f
          [train_loss,name]
        end
        fold_choices<<{fold:fold,treatment:trt,model:winner,training_sessions:training.size,heldout_sessions:heldout.size}
        heldout.each do |s|
          a=index.fetch([s,trt,winner]);b=index.fetch([s,trt,baseline])
          raise 'mismatched group support' unless a[:groups]==b[:groups]
          output<<{session:s,treatment:trt,model:winner,groups:a[:groups],
                   logloss:a[:logloss],baseline_logloss:b[:logloss],
                   delta_logloss:a[:logloss]-b[:logloss],
                   delta_brier:a[:brier]-b[:brier],
                   delta_cost_abs_error:a[:cost_abs_error]-b[:cost_abs_error]}
        end
      end
    end
    results=(1..3).map do |trt|
      group=output.select{|r|r[:treatment]==trt}
      raise '24 heldout sessions required' unless group.size==24
      rng=Random.new(seed+trt)
      values=group.map{|r|r[:delta_logloss]}
      bootstrap=Array.new(draws) do
        Array.new(group.size){values.fetch(rng.rand(group.size))}.sum/group.size.to_f
      end.sort
      {treatment:trt,sessions:group.size,
       chosen:group.group_by{|r|r[:model]}.transform_values{|v|v.size/4},
       logloss:group.sum{|r|r[:logloss]}/group.size.to_f,
       baseline_logloss:group.sum{|r|r[:baseline_logloss]}/group.size.to_f,
       delta_logloss:values.sum/group.size.to_f,
       percentile95:[bootstrap[(draws*0.025).floor],bootstrap[(draws*0.975).floor]],
       delta_brier:group.sum{|r|r[:delta_brier]}/group.size.to_f,
       delta_cost_abs_error:group.sum{|r|r[:delta_cost_abs_error]}/group.size.to_f}
    end
    {sessions:24,groups:5760,candidates:names.size,results:results,fold_choices:fold_choices,
     note:'Exploratory same historical source reused; group independent forecasts, session-level CV. One-period welfare only.'}
  end
  def run(path)
    source_groups=source(path)
    cross_validate(evaluate(source_groups))
  end
end
puts JSON.pretty_generate(Rithm210R23GroupMemoryCV.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
