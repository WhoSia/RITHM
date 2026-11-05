# frozen_string_literal: true
# RITHM-2.10 P3-R15: selected optimal-state U,D calibration under actor independence.
# Works with the SHA-sealed CSV via the P3-R14 source adapter. No subject rows printed.
require_relative 'epoch_independent_welfare'
require 'json'
module Rithm210P3R15JointDiagnostics
  module_function
  KEYS=[:joint_logloss,:next_count_logloss,:pzero,:observed_zero,:pcancel,:observed_cancel,:zero_brier,:cancel_brier,:opposite_residual].freeze
  def convolve(ps)
    ps.reduce([1.0]) do |a,p|
      b=Array.new(a.size+1,0.0)
      a.each_with_index{|v,i|b[i]+=v*(1-p);b[i+1]+=v*p}
      b
    end
  end
  def group_score(row)
    people=row.fetch(:individual)
    a=people.select{|r|r[:route]==1};b=people.select{|r|r[:route]==0}
    raise 'expected four A, two B actors' unless a.size==4 && b.size==2
    pd=convolve(a.map{|r|r[:p]});pu=convolve(b.map{|r|r[:p]})
    d=a.sum{|r|r[:y]};u=b.sum{|r|r[:y]}
    joint=pu[u]*pd[d]
    count=pu.each_with_index.sum{|q,i|pd.each_with_index.sum{|r,j|i-j==u-d ? q*r : 0}}
    zero=(u+d==0 ? 1.0 : 0.0)
    cancel=(u==d && u>0 ? 1.0 : 0.0)
    predzero=pu[0]*pd[0]
    predcancel=(1..2).sum{|k|pu[k]*pd[k]}
    loss=pu.each_with_index.sum{|q,i|pd.each_with_index.sum{|r,j|3*(i-j)**2*q*r}}
    raise 'independent welfare inconsistency' unless (loss-row.fetch(:metrics).fetch(:predicted_loss)).abs<1e-9
    {joint_logloss:-Math.log([joint,1e-300].max),
     next_count_logloss:-Math.log([count,1e-300].max),
     pzero:predzero,observed_zero:zero,pcancel:predcancel,observed_cancel:cancel,
     zero_brier:(predzero-zero)**2,cancel_brier:(predcancel-cancel)**2,
     opposite_residual:row[:metrics][:opposite_route_pair]}
  end
  def means(rows)
    raise 'no rows' if rows.empty?
    KEYS.to_h{|k|[k,rows.sum{|r|r.fetch(:score).fetch(k)}/rows.size.to_f]}.merge(n:rows.size)
  end
  def ci(v)
    a=v.sort
    [a[(a.size*0.025).floor],a[(a.size*0.975).floor]]
  end
  def run(path,draws:20_000,seed:20261105)
    sessions,original=Rithm210EpochIndependentWelfare.source_rows(path)
    rows=original.map{|r|{session:r[:session],model:r[:model],epoch:r[:epoch],score:group_score(r)}}
    by=rows.group_by{|r|[r[:model],r[:epoch]]}
    rng=Random.new(seed)
    comparisons={}
    [:early,:late].each do |epoch|
      base=by.fetch([:baseline,epoch]).group_by{|r|r[:session]}
      calibrated=by.fetch([:epoch20,epoch]).group_by{|r|r[:session]}
      metrics=[:joint_logloss,:next_count_logloss,:zero_brier,:cancel_brier]
      draws_by_metric=metrics.to_h{|k|[k,[]]}
      draws.times do
        sample=Array.new(sessions.size){sessions.fetch(rng.rand(sessions.size))}
        a=sample.flat_map{|s|base.fetch(s,[])}
        b=sample.flat_map{|s|calibrated.fetch(s,[])}
        next if a.empty?
        x=means(a);y=means(b)
        metrics.each{|k|draws_by_metric[k]<<y[k]-x[k]}
      end
      comparisons[epoch]=draws_by_metric.to_h{|k,v|[k,ci(v)]}
    end
    {session_count:sessions.size,selected_groups:original.size/2,
     summary:by.to_h{|key,records|[key.join('_'),means(records)]},
     session_block_bootstrap_delta_ci:comparisons,
     scope:'Exploratory same-source model contrast; conditional on fitted CV predictions; not causal identification.'}
  end
end
puts JSON.pretty_generate(Rithm210P3R15JointDiagnostics.run(ARGV.fetch(0),draws:Integer(ARGV.fetch(1,'20000')))) if $PROGRAM_NAME==__FILE__
