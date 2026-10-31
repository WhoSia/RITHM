# frozen_string_literal: true
# Session-weighted uncertainty estimates for one-step prediction losses.
require 'csv'
module RithmSessionBootstrap
  module_function
  def paired_differences(session_losses, baseline:, candidate:)
    raise ArgumentError,'need observations' if session_losses.empty?
    session_losses.map do |r|
      a=Float(r.fetch(baseline));b=Float(r.fetch(candidate))
      raise ArgumentError,'nonfinite loss' unless a.finite? && b.finite?
      b-a
    end
  end
  def interval(deltas, draws:20_000, seed:20261031)
    raise ArgumentError,'empty' if deltas.empty?
    raise ArgumentError,'draws' unless draws>=100
    rng=Random.new(seed);n=deltas.length
    boot=Array.new(draws) { Array.new(n) { deltas.fetch(rng.rand(n)) }.sum/n.to_f }.sort
    {mean:deltas.sum/n.to_f, lower:boot[((draws-1)*0.025).floor], upper:boot[((draws-1)*0.975).ceil]}
  end
end
