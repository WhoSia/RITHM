# frozen_string_literal: true
# RITHM-2.10 P3-R16: sharp hidden gross-switch bounds from occupancy only.
# Elementary finite combinatorics, NOT claimed as a novel theorem.
module Rithm210OccupancyChurnBounds
  module_function
  def check!(n, a, b)
    raise ArgumentError, 'population must be a positive integer' unless n.is_a?(Integer) && n.positive?
    raise ArgumentError, 'occupancies must be integers in 0..n' unless [a, b].all? { |v| v.is_a?(Integer) && v.between?(0, n) }
  end
  # a = old A count, b = next A count; u = B->A, d = A->B.
  def possible_pairs(n:, a:, b:)
    check!(n, a, b)
    d0 = [0, a-b].max
    d1 = [a, n-b].min
    (d0..d1).map { |d| {u:b-a+d, d:d} }
  end
  def gross_range(n:, a:, b:)
    check!(n, a, b)
    {minimum:(b-a).abs, maximum:[a+b, 2*n-a-b].min}
  end
  def possible_gross(n:, a:, b:)
    possible_pairs(n:n, a:a, b:b).map { |p| p[:u]+p[:d] }
  end
  # k is a REAL per-switch resource cost, not psychological utility.
  def resource_bounds(n:, path:, k:)
    raise ArgumentError, 'path must have at least two occupancies' unless path.is_a?(Array) && path.size >= 2
    raise ArgumentError, 'k must be nonnegative' unless k.is_a?(Numeric) && k.real? && k.finite? && k >= 0
    pair_bounds=path.each_cons(2).map { |a,b| gross_range(n:n,a:a,b:b) }
    lo=pair_bounds.sum { |x| x[:minimum] }
    hi=pair_bounds.sum { |x| x[:maximum] }
    {min_gross:lo,max_gross:hi,min_switch_cost:k*lo,max_switch_cost:k*hi}
  end
  def congestion_cost(n_a, n:6)
    raise ArgumentError, 'n_a out of bounds' unless n_a.is_a?(Integer) && n_a.between?(0,n)
    n_a*n_a+2*(n-n_a)*(n-n_a)
  end
end
