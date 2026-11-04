# frozen_string_literal: true
# P3-R6: heldout activity-targeted evaluation from the previously published actor model.
# Individual participant rows remain in Drive; only aggregate evaluations are output.
require_relative '../p2/online_actor_history'
require 'digest'
require 'json'
module Rithm210ActivityEventCV
  module_function
  SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'
  def event_probabilities(people,p)
    up=[];down=[]
    people.each_with_index do |r,i|
      (r['RouteA'].to_i==1 ? down : up)<<p[i]
    end
    pu=Rithm210OnlineIdentity.convolve(up)
    pd=Rithm210OnlineIdentity.convolve(down)
    none=pu[0]*pd[0]
    cancel=(1..[up.length,down.length].min).sum{|j|pu[j]*pd[j]}
    next_loss=pu.each_with_index.sum do |a,u|
      pd.each_with_index.sum{|b,d|3*(down.size+u-d-4)**2*a*b}
    end
    {none:none,cancel:cancel,next_loss:next_loss}
  end
  def binary_score(p,y)
    raise 'probability invalid' unless p.between?(0,1)
    {brier:(p-y)**2,logloss:-Math.log([y==1 ? p : 1-p,1e-300].max)}
  end
  def run(csv)
    raise 'source hash mismatch' unless Digest::SHA256.file(csv).hexdigest==SHA
    groups=Rithm210OnlineIdentity.source(csv)
    sessions=groups.keys.map(&:first).uniq.sort
    fold=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    rows=[]
    6.times do |f|
      held=sessions.select{|s|fold[s]==f}
      fitted=Rithm210OnlineIdentity.train(groups,held)
      history=Hash.new{|h,k|h[k]=[0,0]}
      keys=groups.keys.select{|k|held.include?(k[0])}.sort_by{|s,section,g,t|[s,section,t,g]}
      keys.each do |s,section,g,t|
        actors=groups.fetch([s,section,g,t])
        base=actors.map{|r|Rithm210OnlineIdentity.probability(fitted,r)}
        models={baseline:base}
        [20,80].each do |strength|
          models["online_#{strength}".to_sym]=actors.each_with_index.map do |r,i|
            h=history[[s,section,r['ID'].to_i]]
            Rithm210OnlineIdentity.online_probability(base[i],h,strength.to_f)
          end
        end
        u=actors.sum{|r|r['switchBtoAWill'].to_i}
        d=actors.sum{|r|r['switchAtoBWill'].to_i}
        n=actors.first['NumA'].to_i
        raise 'invalid next occupancy' unless actors.first['NumAnext'].to_i==n+u-d
        observed_loss=3*(n+u-d-4)**2
        models.each do |model,prob|
          predicted=event_probabilities(actors,prob)
          event_none=(u+d==0 ? 1 : 0)
          event_cancel=(u>0 && d==u ? 1 : 0)
          a=binary_score(predicted[:none],event_none)
          b=binary_score(predicted[:cancel],event_cancel)
          rows<<{session:s,period:t,treatment:actors.first['trt'].to_i,
            current_a:n,model:model,
            no_switch_brier:a[:brier],no_switch_logloss:a[:logloss],
            cancel_brier:b[:brier],cancel_logloss:b[:logloss],
            no_switch_pred:predicted[:none],no_switch_obs:event_none,
            cancel_pred:predicted[:cancel],cancel_obs:event_cancel,
            welfare_mse:(predicted[:next_loss]-observed_loss)**2}
        end
        # No future leakage: current outcome enters after every period-t forecast.
        actors.each do |r|
          h=history[[s,section,r['ID'].to_i]]
          h[0]+=r['switchWill'].to_i;h[1]+=1
        end
      end
    end
    raise 'coverage mismatch' unless rows.size==5616*3
    stats=->(rr){keys=[:no_switch_brier,:no_switch_logloss,:cancel_brier,:cancel_logloss,
      :no_switch_pred,:no_switch_obs,:cancel_pred,:cancel_obs,:welfare_mse]
      {n:rr.size}.merge(keys.to_h{|k|[k,rr.sum{|r|r[k]}/rr.size.to_f]})}
    {n:5616,overall:rows.group_by{|r|r[:model]}.transform_values(&stats),
      optimal:rows.select{|r|r[:current_a]==4}.group_by{|r|r[:model]}.transform_values(&stats),
      full_optimal_epoch:rows.select{|r|r[:current_a]==4 && r[:treatment]==3 && (r[:period]<=10 || r[:period]>=30)}.
        group_by{|r|[r[:model],r[:period]<=10 ? :early : :late]}.to_h{|k,a|[k.join('_'),stats.call(a)]},
      session_rows:rows.group_by{|r|[r[:session],r[:model]]}.to_h{|k,a|[k.join('_'),stats.call(a)]}}
  end
end
puts JSON.pretty_generate(Rithm210ActivityEventCV.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
