# frozen_string_literal: true
# SHARP identification bounds if only the six-person route-A OCCUPANCY path is observed.
# These are NOT bounds on real switching-resource costs unless theta is externally specified.
module Rithm210OccupancyEquivalence
  module_function

  def legal_count(n)
    raise ArgumentError,'occupancy outside 0..6' unless n.is_a?(Integer) && n.between?(0,6)
  end

  def feasible_turnovers(from:,to:)
    legal_count(from);legal_count(to)
    delta=to-from
    umin=[0,delta].max
    umax=[6-from,to].min
    (umin..umax).map{|u|{up:u,down:u-delta,gross:2*u-delta}}
  end

  def sharp_bounds(from:,to:)
    a=feasible_turnovers(from:from,to:to)
    {minimum:a.first.fetch(:gross),maximum:a.last.fetch(:gross),
      possible:a.map{|x|x[:gross]},count:a.length}
  end

  def construct(previous:,up:,down:)
    raise ArgumentError,'six binary choices required' unless previous.is_a?(Array) &&
      previous.length==6 && previous.all?{|v|v==0 || v==1}
    from=previous.sum
    raise ArgumentError,'infeasible switching' unless
      up.is_a?(Integer)&&down.is_a?(Integer)&&
      up.between?(0,6-from)&&down.between?(0,from)
    next_choices=previous.dup
    previous.each_index.select{|i|previous[i]==0}.first(up).each{|i|next_choices[i]=1}
    previous.each_index.select{|i|previous[i]==1}.first(down).each{|i|next_choices[i]=0}
    raise 'construction mismatch' unless next_choices.sum==from+up-down
    next_choices
  end

  def path_bounds(occupancies)
    raise ArgumentError,'at least two observations required' unless
      occupancies.is_a?(Array)&&occupancies.length>=2
    occupancies.each{|n|legal_count(n)}
    steps=occupancies.each_cons(2).map{|a,b|sharp_bounds(from:a,to:b)}
    {periods:steps.length,minimum:steps.sum{|x|x[:minimum]},
      maximum:steps.sum{|x|x[:maximum]},step_bounds:steps}
  end

  def same_cost_but_different_switches?
    zero=construct(previous:[1,1,1,1,0,0],up:0,down:0)
    two=construct(previous:[1,1,1,1,0,0],up:1,down:1)
    four=construct(previous:[1,1,1,1,0,0],up:2,down:2)
    [zero,two,four].all?{|a|a.sum==4} &&
      [zero,two,four].map{|a|a.each_with_index.count{|x,i|x!=[1,1,1,1,0,0][i]}}==[0,2,4]
  end
end
