# frozen_string_literal: true
require_relative 'residual_negative_control'
module Rithm210ActorCalibration
  module_function
  def epoch(period)
    return :early if period <= 10
    return :late if period >= 30
    :middle
  end
  def score(path)
    groups = Rithm210ResidualNegativeControl.read_groups(path)
    sessions = groups.keys.map(&:first).uniq.sort
    folds = sessions.each_with_index.to_h { |s,i| [s,i%6] }
    rows = []
    6.times do |f|
      model = Rithm210ResidualNegativeControl.fit(groups,folds,f)
      groups.each do |(s,section,group,period),people|
        next unless folds[s]==f
        people.each do |r|
          p = Rithm210ResidualNegativeControl.probability(model,r)
          y = r.fetch('switchWill').to_i
          raise 'invalid y' unless [0,1].include?(y)
          rows << {session:s,trt:r['trt'].to_i,route:r['RouteA'].to_i,
            informed:r['Informed'].to_i,epoch:epoch(period),p:p,y:y,
            squared:(p-y)**2,error:y-p}
        end
      end
    end
    raise 'unexpected people' unless rows.size==33_696
    agg=->(a){n=a.size; {n:n,mean_pred:a.sum{|x|x[:p]}/n.to_f,
      switch_rate:a.sum{|x|x[:y]}/n.to_f,
      calibration_bias:a.sum{|x|x[:error]}/n.to_f,
      brier:a.sum{|x|x[:squared]}/n.to_f}}
    by=->(keys){rows.group_by{|r|keys.map{|k|r[k]}}.map{|k,a|{strata:k,**agg.call(a)}}.sort_by{|v|v[:strata].map(&:to_s)}}
    {global:agg.call(rows),treatment:by.call([:trt]),
      treatment_epoch:by.call([:trt,:epoch]),
      treatment_informed_route:by.call([:trt,:informed,:route])}
  end
end
if __FILE__==$PROGRAM_NAME
  puts JSON.pretty_generate(Rithm210ActorCalibration.score(ARGV.fetch(0)))
end
