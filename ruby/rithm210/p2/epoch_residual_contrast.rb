# frozen_string_literal: true
require_relative 'epoch_conditioned_model'
module Rithm210EpochResidualContrast
  module_function
  def matched(records)
    by_time=records.group_by{|r|[r[:session],r[:section],r[:period]]}
    by_time.values.flat_map do |a|
      a.flat_map do |r|
        other=a.reject{|q|q[:group]==r[:group]}
        next [] if other.empty?
        between=r[:ru]*other.sum{|q|q[:rd]}/other.size.to_f
        [{session:r[:session],n:1,within:r[:ru]*r[:rd],between:between,
          difference:r[:ru]*r[:rd]-between}]
      end
    end
  end
  def resample(rows,metric,draws:20_000,seed:20261103)
    by=rows.group_by{|r|r[:session]}.values.map do |a|
      {n:a.size,value:a.sum{|r|r.fetch(metric)}}
    end
    n=by.size;rng=Random.new(seed)
    point=by.sum{|r|r[:value]}/by.sum{|r|r[:n]}.to_f
    bs=Array.new(draws) do
      a=Array.new(n){by.fetch(rng.rand(n))}
      a.sum{|r|r[:value]}/a.sum{|r|r[:n]}.to_f
    end.sort
    {mean:point,lower:bs[(draws*0.025).floor],upper:bs[(draws*0.975).floor]}
  end
  def execute(path,draws:20_000)
    groups=Rithm210ResidualNegativeControl.read_groups(path)
    sessions=groups.keys.map(&:first).uniq.sort
    folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
    res={baseline:[],epoch:[]}
    6.times do |f|
      model=Rithm210EpochConditionedModel.train(groups,folds,f)
      groups.each do |(s,section,g,t),people|
        next unless folds.fetch(s)==f
        u=people.sum{|r|r['switchBtoAWill'].to_i};d=people.sum{|r|r['switchAtoBWill'].to_i}
        [false,true].each do |conditioned|
          p=->(r){Rithm210EpochConditionedModel.probability(model,r,t,conditional:conditioned)}
          eu=people.select{|r|r['RouteA'].to_i==0}.sum(&p)
          ed=people.select{|r|r['RouteA'].to_i==1}.sum(&p)
          name=conditioned ? :epoch : :baseline
          res[name]<<{session:s,section:section,group:g,period:t,ru:u-eu,rd:d-ed}
        end
      end
    end
    paired=res.transform_values{|v|matched(v)}
    raise 'matched counts differ' unless paired[:baseline].size==paired[:epoch].size && paired[:baseline].size==5148
    diff=paired[:baseline].zip(paired[:epoch]).map do |b,e|
      raise 'session order mismatch' unless b[:session]==e[:session]
      {session:b[:session],difference:e[:difference]-b[:difference]}
    end
    {groups:5616,matched:5148,
      baseline:[:within,:between,:difference].to_h{|m|[m,resample(paired[:baseline],m,draws:draws)]},
      epoch:[:within,:between,:difference].to_h{|m|[m,resample(paired[:epoch],m,draws:draws)]},
      epoch_minus_baseline_matched_difference:resample(diff,:difference,draws:draws)}
  end
end
puts JSON.pretty_generate(Rithm210EpochResidualContrast.execute(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
