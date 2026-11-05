# frozen_string_literal: true
# R20: model comparison with full SESSION paired resampling, not group pseudoreplication.
# Original human source was reused for exploratory development; not a novel trial.
module Rithm210R20SessionContrast
  module_function
  METRICS=[:logloss,:brier,:cost_abs_error,:cost_bias].freeze
  def compare(rows,treatment:,model:,baseline: :own_route_frequency,draws:20_000,seed:20261106)
    raise ArgumentError,'positive draws' unless draws.is_a?(Integer)&&draws.positive?
    raise ArgumentError,'same model' if model.to_s==baseline.to_s
    group=rows.select{|r|r.fetch(:treatment)==treatment}
    model_rows=group.select{|r|r.fetch(:model).to_s==model.to_s}
    base_rows=group.select{|r|r.fetch(:model).to_s==baseline.to_s}
    chosen=model_rows.to_h{|r|[r.fetch(:session),r]}
    control=base_rows.to_h{|r|[r.fetch(:session),r]}
    raise ArgumentError,'duplicate session/model' unless chosen.size==model_rows.size&&control.size==base_rows.size
    raise ArgumentError,'unpaired or insufficient independent sessions' unless chosen.keys.sort==control.keys.sort&&chosen.size>=2
    ids=chosen.keys.sort
    differences=ids.map do |id|
      a=chosen.fetch(id);b=control.fetch(id)
      raise ArgumentError,'unmatched group count' unless a.fetch(:groups)==b.fetch(:groups)
      METRICS.to_h{|k|[k,a.fetch(k)-b.fetch(k)]}
    end
    result=METRICS.to_h do |metric|
      values=differences.map{|r|r.fetch(metric)}
      mean=values.sum/values.size.to_f
      rng=Random.new(seed)
      samples=Array.new(draws) do
        Array.new(values.size){values.fetch(rng.rand(values.size))}.sum/values.size.to_f
      end.sort
      [metric,{mean_difference:mean,
        percentile95:[samples[(draws*0.025).floor],samples[(draws*0.975).floor]],
        sessions_model_better:values.count{|x|x<0}}]
    end
    {treatment:treatment,model:model,baseline:baseline,sessions:ids.size,draws:draws,
      metrics:result,scope:'Exploratory paired per-session one-period scores. Same historical data repeatedly inspected; no causal or confirmatory conclusion.'}
  end
end
