# frozen_string_literal: true
# Session-paired exploratory Brier contrast for exact prior-only SSMq.
module Rithm210R19SSMSessionContrast
  module_function
  def compare(rows,treatment:,informed:,model:,baseline:'own_route_frequency',draws:10_000,seed:20261105)
    raise ArgumentError,'draw count' unless draws.is_a?(Integer)&&draws>0
    candidates=rows.select{|r|r.fetch(:treatment)==treatment&&r.fetch(:informed)==informed}
    by=candidates.group_by{|r|[r.fetch(:session),r.fetch(:model)]}
    raise ArgumentError,'duplicate session/model' unless by.values.all?{|a|a.size==1}
    ids=candidates.select{|r|r[:model]==model}.map{|r|r[:session]}.sort
    controls=candidates.select{|r|r[:model]==baseline}.map{|r|r[:session]}.sort
    raise ArgumentError,'paired sessions needed' unless ids==controls&&ids.size>=2
    effects=ids.map do |sid|
      a=by.fetch([sid,model]).first
      b=by.fetch([sid,baseline]).first
      raise ArgumentError,'unequal session support' unless a.fetch(:n)==b.fetch(:n)
      a.fetch(:brier).to_f-b.fetch(:brier).to_f
    end
    rng=Random.new(seed)
    boot=Array.new(draws) do
      Array.new(effects.size){effects.fetch(rng.rand(effects.size))}.sum/effects.size
    end.sort
    {treatment:treatment,informed:informed,model:model,baseline:baseline,
     sessions:ids.size,mean_brier_difference:effects.sum/effects.size,
     bootstrap_percentile95:[boot[(draws*0.025).floor],boot[(draws*0.975).floor]],
     sessions_ssm_worse:effects.count{|v|v>0},
     caveat:'Repeatedly examined same source, exploratory session bootstrap; not confirmatory model evidence.'}
  end
end
