# frozen_string_literal: true
# Fixed-gamma original-source subgroup audit. Selection of .30 predates this audit.
require_relative 'nested_gamma_cv'
require 'json'
module Rithm210TreatmentEpochCV
  module_function
  def epoch(period)
    return 'early' if period<=10
    return 'late' if period>=30
    'middle'
  end
  def predict(groups)
    m=Rithm210NestedGammaCV
    sessions=groups.keys.map(&:first).uniq.sort
    raise 'wrong sessions' unless sessions.length==24
    folds=m.split(sessions,6)
    records=[]
    6.times do |fold|
      fit=m.train_model(groups,sessions.reject{|s|folds[s]==fold})
      groups.each do |key,people|
        s,section,g,period=key
        next unless folds[s]==fold
        pa=people.select{|r|r['RouteA'].to_i==1}.map{|r|m.probability(fit,r)}
        pb=people.select{|r|r['RouteA'].to_i==0}.map{|r|m.probability(fit,r)}
        u=people.sum{|r|r['switchBtoAWill'].to_i}
        d=people.sum{|r|r['switchAtoBWill'].to_i}
        baseline=Rithm210LatentCV.joint_and_count(pa,pb,u,d,0.0)
        candidate=Rithm210LatentCV.joint_and_count(pa,pb,u,d,0.30)
        records<<{session:s,fold:fold,section:section,group:g,period:period,
          treatment:people.first['trt'].to_i,epoch:epoch(period),
          joint0:baseline[0],count0:baseline[1],joint1:candidate[0],count1:candidate[1]}
      end
    end
    raise 'wrong scored groups' unless records.length==5616
    records
  end
  def bootstrap(rows,key:,draws:10_000,seed:20261103)
    raise 'empty rows' if rows.empty?
    by=rows.group_by{|r|r[:session]}.values.map{|a|{n:a.size,sum:a.sum{|r|r.fetch(key)}}}
    rng=Random.new(seed)
    point=by.sum{|r|r[:sum]}/by.sum{|r|r[:n]}.to_f
    samples=Array.new(draws) do
      z=Array.new(by.size){by.fetch(rng.rand(by.size))}
      z.sum{|r|r[:sum]}/z.sum{|r|r[:n]}.to_f
    end.sort
    {mean:point,lower:samples[(draws*0.025).floor],upper:samples[(draws*0.975).floor],clusters:by.size}
  end
  def report(path,draws:10_000)
    rows=predict(Rithm210ResidualNegativeControl.read_groups(path))
    rows.each{|r|r[:joint_delta]=r[:joint1]-r[:joint0];r[:count_delta]=r[:count1]-r[:count0]}
    categories={all:rows}
    rows.group_by{|r|r[:treatment]}.each{|t,a|categories["trt_#{t}"]=a}
    rows.group_by{|r|r[:epoch]}.each{|ep,a|categories["epoch_#{ep}"]=a}
    rows.group_by{|r|[r[:treatment],r[:epoch]]}.each{|(t,e),a|categories["trt_#{t}_#{e}"]=a}
    stats=categories.to_h do |name,a|
      [name,{n:a.size,joint0:a.sum{|r|r[:joint0]}/a.size.to_f,
        joint1:a.sum{|r|r[:joint1]}/a.size.to_f,
        joint_delta:bootstrap(a,key: :joint_delta,draws:draws),
        count_delta:bootstrap(a,key: :count_delta,draws:draws)}]
    end
    {observations:rows.size,session_count:rows.map{|r|r[:session]}.uniq.size,
      gamma_comparison:[0.0,0.30],stats:stats}
  end
end
puts JSON.pretty_generate(Rithm210TreatmentEpochCV.report(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
