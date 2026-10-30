# frozen_string_literal: true
# A sharp 2-world information bound inside the source's six-player routing game.
# Conditional on having chosen A and observed profit 5, both worlds fit the
# author's random trip-value support [6,16].
worlds = [{m: 0, value: 6}, {m: 5, value: 11}]
res = worlds.map do |w|
  cost_a = w[:m] + 1
  cost_b_if_alone_switches = 2 * (6 - w[:m])
  {m: w[:m], observed_payoff_a: w[:value] - cost_a,
   alternative_payoff_b: w[:value] - cost_b_if_alone_switches}
end
raise 'different on-path observations' unless res.map { |w| w[:observed_payoff_a] }.uniq == [5]
raise 'incorrect off-path payoffs' unless res.map { |w| w[:alternative_payoff_b] } == [-6, 9]
# In the first world, switching costs 11. In the second, staying costs 4.
# A private-information policy switches with probability p; worst-case regret:
# max(11p, 4(1-p)). The intersection minimizes the upper envelope.
p = Rational(4, 15)
bound = [11 * p, 4 * (1 - p)].max
raise 'bad minimax' unless bound == Rational(44, 15)
# Independent finite grid certifies the crossing is a minimum.
(0..1500).each do |j|
  q = Rational(j, 1500)
  raise 'counterexample to lower bound' if [11 * q, 4 * (1 - q)].max < bound
end
puts "observed_A_payoff=5; worlds=#{res}; minimax_switch_probability=#{p}; worst_case_regret=#{bound}"
