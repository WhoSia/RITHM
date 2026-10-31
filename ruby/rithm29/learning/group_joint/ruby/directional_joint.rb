# frozen_string_literal: true
module RithmDirectionalJoint
  module_function
  def bernoulli_count(probabilities)
    probabilities.reduce([1.0]) do |dist, p|
      raise ArgumentError, 'invalid probability' unless p.finite? && p.between?(0.0, 1.0)
      out = Array.new(dist.size + 1, 0.0)
      dist.each_with_index do |mass, count|
        out[count] += mass * (1.0-p)
        out[count+1] += mass * p
      end
      out
    end
  end
  def distribution(previous:, probabilities:)
    raise ArgumentError, 'length mismatch' unless previous.size == probabilities.size
    raise ArgumentError, 'invalid previous route' unless previous.all? { |x| x == 0 || x == 1 }
    up = previous.each_index.filter_map { |i| probabilities[i] if previous[i] == 0 }
    down = previous.each_index.filter_map { |i| 1.0-probabilities[i] if previous[i] == 1 }
    pu = bernoulli_count(up)
    pd = bernoulli_count(down)
    pu.map { |u| pd.map { |d| u*d } }
  end
  def probability(joint, u, d)
    return 0.0 unless u.is_a?(Integer) && d.is_a?(Integer) && u >= 0 && d >= 0
    joint.fetch(u, []).fetch(d, 0.0)
  end
  def expectation(joint)
    total = joint.flatten.sum
    raise ArgumentError, 'not normalized' unless (total-1.0).abs < 1e-8
    gross = net_abs = cancelled = 0.0
    joint.each_with_index do |row, u|
      row.each_with_index do |mass, d|
        gross += mass*(u+d)
        net_abs += mass*(u-d).abs
        cancelled += mass if u > 0 && d > 0
      end
    end
    {gross:gross, net_abs:net_abs, cancellation:cancelled}
  end
end
