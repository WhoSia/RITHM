# frozen_string_literal: true
# Exact joint-turnover identity separating individual changes and aligned pair terms.
# For n_A(t)=4: next-period social congestion excess is 3(U-D)^2.
module Rithm210PairwiseWelfare
  module_function

  def choose2(k)
    raise ArgumentError, 'negative count' unless k.is_a?(Integer) && k >= 0
    k * (k - 1) / 2
  end

  def decompose(up:,down:,current_a:4)
    unless current_a.is_a?(Integer) && current_a.between?(0,6) &&
        up.is_a?(Integer) && down.is_a?(Integer) &&
        up.between?(0,6-current_a) && down.between?(0,current_a)
      raise ArgumentError, 'infeasible six-person transition'
    end
    gross=up+down
    same_direction_pairs=choose2(up)+choose2(down)
    opposing_pairs=up*down
    squared_net=gross+2*(same_direction_pairs-opposing_pairs)
    raise 'pairwise identity broken' unless squared_net==(up-down)**2
    current_loss=3*(current_a-4)**2
    next_loss=3*(current_a+up-down-4)**2
    drift=6*(current_a-4)*(up-down)+3*squared_net
    raise 'cost identity broken' unless next_loss-current_loss==drift
    {gross:gross,same_direction_pairs:same_direction_pairs,
      opposing_pairs:opposing_pairs,pair_balance:same_direction_pairs-opposing_pairs,
      squared_net:squared_net,linear_drift:6*(current_a-4)*(up-down),
      next_loss:next_loss,loss_change:drift}
  end

  def mean_moments(records)
    raise ArgumentError, 'no transitions' if records.empty?
    n=records.size.to_f
    keys=[:gross,:same_direction_pairs,:opposing_pairs,:pair_balance,
      :squared_net,:next_loss,:loss_change]
    means=keys.to_h{|key|[key,records.sum{|r|r.fetch(key)}/n]}
    raise 'expected joint identity' unless
      (means[:squared_net]-means[:gross]-2*means[:pair_balance]).abs<1e-10
    means.merge(n:records.size)
  end
end
