# frozen_string_literal: true
require_relative 'composition_court'
# Exact prefix-capacity bound ONLY for all-release-zero, preemptive divisible
# integer work, no setup loss, no per-round upper bound on purchased boost.
module RithmPrefixBound
  module_function
  def min_boost(bundles, capacities:)
    bundles.each { |b| RithmCompositionCourt.validate!(b) }
    jobs = bundles.map { |b| b.fetch('receipt') }
    keys = jobs.map { |j| [j.fetch('person'),j.fetch('episode')] }
    raise 'duplicate obligation' unless keys.uniq.length == keys.length
    raise 'capacity' unless capacities.all? { |c| c.is_a?(Integer) && c >= 0 }
    raise 'deadline' if jobs.any? { |j| j['deadline'] < 1 || j['deadline'] > capacities.length }
    capacities.each_index.map do |t|
      due = jobs.sum { |j| j.fetch('deadline') <= t+1 ? j.fetch('demand') : 0 }
      due - capacities.first(t+1).sum
    end.push(0).max
  end
end
