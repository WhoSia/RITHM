# frozen_string_literal: true
# Online Bayes posterior over a fixed actor-specific latent sample size q_i.
# Declared lapse prevents zero-support collapse; source-free method.
require_relative 'r19_ssm_exact'
module Rithm210R19PersistentQFilter
  class Filter
    attr_reader :weights,:qmax,:lapse,:last_probabilities
    def initialize(qmax:3,lapse:0.02)
      raise ArgumentError,'qmax1..9 required' unless qmax.is_a?(Integer)&&qmax.between?(1,9)
      raise ArgumentError,'lapse [0,1]' unless lapse.is_a?(Numeric)&&lapse.finite?&&lapse.between?(0,1)
      @qmax=qmax;@lapse=lapse.to_f
      @weights=Array.new(qmax,1.0/qmax)
      @last_probabilities=nil
    end
    def predict(history:,informed:)
      raise 'prior choice prediction not yet updated' if @last_probabilities
      @last_probabilities=(1..@qmax).map do |q|
        exact=Rithm210R19SSMExact.probability(history:history,q:q,informed:informed).to_f
        (1-@lapse)*exact+0.5*@lapse
      end
      @weights.zip(@last_probabilities).sum{|weight,p|weight*p}
    end
    def update(route_a:)
      raise ArgumentError,'boolean outcome required' unless [true,false].include?(route_a)
      raise 'predict before update' unless @last_probabilities
      posterior=@weights.zip(@last_probabilities).map{|w,p|w*(route_a ? p : (1-p))}
      total=posterior.sum
      raise 'zero posterior evidence' unless total.positive?
      @weights=posterior.map{|v|v/total}
      @last_probabilities=nil
      @weights.dup
    end
  end
end
