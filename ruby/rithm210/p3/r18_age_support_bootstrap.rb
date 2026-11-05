# frozen_string_literal: true
require_relative 'r18_observable_age_support'
module Rithm210R18AgeSupportBootstrap
  module_function
  def summarize(rows,draws:20_000,seed:20261105)
    raise ArgumentError,'draw count' unless draws.is_a?(Integer)&&draws>0
    by=rows.group_by{|r|r.fetch(:session)}
    raise ArgumentError,'sessions' if by.size<2
    ids=by.keys.sort
    values=ids.to_h do |s|
      [s,[:early,:late].to_h do |epoch|
        x=by[s].select{|r|r.fetch(:epoch)==epoch}
        [epoch,[x.count{|r|!r.fetch(:unchanged)},x.size]]
      end]
    end
    rate=lambda do |selection,epoch|
      den=selection.sum{|s|values[s][epoch][1]}
      raise ArgumentError,'empty period' if den==0
      selection.sum{|s|values[s][epoch][0]}.to_f/den
    end
    rng=Random.new(seed)
    samples=Array.new(draws) do
      selection=Array.new(ids.size){ids[rng.rand(ids.size)]}
      rate.call(selection,:late)-rate.call(selection,:early)
    end.sort
    {sessions:ids.size,early:rate.call(ids,:early),late:rate.call(ids,:late),
      difference:rate.call(ids,:late)-rate.call(ids,:early),
      interval95:[samples[(0.025*draws).floor],samples[(0.975*draws).floor]],
      draws:draws,warning:'Descriptive same-source session resampling, not causal evidence.'}
  end
end
