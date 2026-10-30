# frozen_string_literal: true
# Independent Ruby replay of authors' EWA-lite Appendix A.4 maximum likelihood.
# ruby ewa_real_mle.rb /path/to/data_task_all_switch_230705.csv
require 'csv'
require 'json'
require_relative 'learning_models'
path = ARGV.fetch(0)
rows = CSV.foreach(path, headers: true).select do |r|
  r['trt'].to_i <= 3 && ![2, 101].include?(r['session'].to_i) && r['section'].to_i <= 4
end
raise 'unexpected rows' unless rows.size == 34_560
people = rows.group_by { |r| [r['trt'], r['session'], r['section'], r['Group'], r['ID']] }
raise 'unexpected persons' unless people.size == 864
samples = []
people.each do |_key, rs|
  rs.sort_by! { |r| r['Period'].to_i }
  raise 'not forty sequential periods' unless rs.map { |r| r['Period'].to_i } == (1..40).to_a
  informed = rs.first['Informed'].to_i == 1
  model = RithmLearningModels::EWA.new(informed: informed, lambda: 1.0)
  rs.each do |r|
    p = model.probability_a
    delta = Math.log(p / (1.0 - p))
    chosen = r['RouteA'].to_i
    samples << [delta, chosen]
    model.update(route_a: chosen, payoff: r['profit'].to_f,
                 total_a: informed ? r['NumA'].to_i : nil)
  end
end
def neg_ll(samples, lambda)
  samples.sum do |delta, chosen|
    z = (chosen == 1 ? 1 : -1) * lambda * delta
    Math.log(1 + Math.exp(-z.abs)) + [-z, 0.0].max
  end / samples.size
end
a, b = 0.0, 16.0
inv_phi = (Math.sqrt(5.0) - 1.0) / 2.0
c, d = b - inv_phi * (b - a), a + inv_phi * (b - a)
fc, fd = neg_ll(samples, c), neg_ll(samples, d)
45.times do
  if fc <= fd
    b, d, fd = d, c, fc
    c = b - inv_phi * (b - a)
    fc = neg_ll(samples, c)
  else
    a, c, fc = c, d, fd
    d = a + inv_phi * (b - a)
    fd = neg_ll(samples, d)
  end
end
estimate = (a + b) / 2.0
puts JSON.pretty_generate({persons: people.size, observations: samples.size,
                           lambda_mle: estimate, in_sample_logloss: neg_ll(samples, estimate)})
