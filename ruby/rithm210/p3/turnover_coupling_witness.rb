# frozen_string_literal: true
# P3-R16 illustrative NONIDENTIFICATION, not new theorem or empirical strategy.
# Same route occupancy AND each actor's switching marginal; distinct group gross-risk.
module Rithm210TurnoverCouplingWitness
  module_function
  PREVIOUS=[1,1,1,1,0,0].freeze
  def distributions
    shock={[]=>Rational(1,2),[0,1,4,5]=>Rational(1,2)}
    compensated=[0,1].product([4,5]).to_h{|a,b|[[a,b],Rational(1,4)]}
    {shock:shock,compensated:compensated}
  end
  def summarize(dist)
    raise ArgumentError,'empty distribution' if dist.empty?
    raise ArgumentError,'probability mass != 1' unless dist.values.sum==1
    dist.each do |actors,weight|
      raise ArgumentError,'invalid switch set' unless actors.uniq==actors && actors.all?{|i|i.is_a?(Integer)&&i.between?(0,5)}
      raise ArgumentError,'negative weight' if weight<0
    end
    marginal=(0...6).map{|i|dist.sum{|actors,w|actors.include?(i) ? w : 0}}
    occupancy=dist.to_h do |actors,w|
      next_state=PREVIOUS.each_with_index.map{|old,i|actors.include?(i) ? 1-old : old}
      [actors,{probability:w,next_occupancy:next_state.sum,gross:actors.size}]
    end
    eg=occupancy.values.sum{|x|x[:probability]*x[:gross]}
    eg2=occupancy.values.sum{|x|x[:probability]*x[:gross]**2}
    {marginal:marginal,
     next_occupancy_distribution:occupancy.values.group_by{|x|x[:next_occupancy]}.to_h{|n,rows|[n,rows.sum{|r|r[:probability]}]},
     expected_gross:eg,gross_variance:eg2-eg*eg,expected_gross_squared:eg2,
     p_gross_ge_four:occupancy.values.sum{|r|r[:gross]>=4 ? r[:probability] : 0}}
  end
  def witness
    distributions.transform_values{|dist|summarize(dist)}
  end
end
