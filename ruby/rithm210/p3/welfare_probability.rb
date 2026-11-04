# frozen_string_literal: true
require_relative '../p2/online_actor_history'
require_relative 'experimental_welfare'
module Rithm210WelfareProbability
  module_function
  def law(people, probabilities, current_a)
    ups=[]
    downs=[]
    people.each_with_index do |person,i|
      if person['RouteA'].to_i==1
        downs << probabilities.fetch(i)
      else
        ups << probabilities.fetch(i)
      end
    end
    up=Rithm210OnlineIdentity.convolve(ups)
    down=Rithm210OnlineIdentity.convolve(downs)
    result=Hash.new(0.0)
    up.each_with_index do |p,u|
      down.each_with_index do |q,d|
        result[Rithm210ExperimentalWelfare.excess(current_a+u-d)]+=p*q
      end
    end
    raise 'not normalized' unless (result.values.sum-1).abs<1e-9
    result
  end
  def scoring(law,actual_excess)
    mean=law.sum{|value,p|value*p}
    p=law.fetch(actual_excess,0.0)
    raise 'zero probability' unless p>0
    {logloss:-Math.log(p),squared_error:(mean-actual_excess)**2,mean:mean}
  end
end
