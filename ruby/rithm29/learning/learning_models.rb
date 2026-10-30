# frozen_string_literal: true
# Noussair-Qiao online Appendices A/B learning rules; Ruby standard library.
module RithmLearningModels
  module_function
  def route_cost(route_a,m)
    route_a==1 ? m+1 : 2*(6-m)
  end
  def compatible_other_counts(route_a:,payoff:,value_min:6.0,value_max:16.0)
    raise ArgumentError,'route' unless [0,1].include?(route_a)
    (0..5).select { |m| v=Float(payoff)+route_cost(route_a,m); v>=value_min-1e-10 && v<=value_max+1e-10 }
  end
  def belief(route_a:,payoff:)
    possibilities=compatible_other_counts(route_a:route_a,payoff:payoff)
    raise ArgumentError,'incompatible payoff' if possibilities.empty?
    Array.new(6) { |m| possibilities.include?(m) ? 1.0/possibilities.size : 0.0 }
  end
  def inferred_counterfactual(route_a:,payoff:)
    probs=belief(route_a:route_a,payoff:payoff)
    Float(payoff)+(0..5).sum { |m| probs[m]*(route_cost(route_a,m)-route_cost(1-route_a,m)) }
  end
  def informed_counterfactual(route_a:,payoff:,total_a:)
    m=Integer(total_a)-route_a
    raise ArgumentError,'invalid occupancy' unless (0..5).cover?(m)
    Float(payoff)+route_cost(route_a,m)-route_cost(1-route_a,m)
  end
  class EWA
    attr_reader :n,:attractions,:history
    def initialize(informed:,lambda:1.0)
      @informed,@lambda=informed,Float(lambda)
      @n,@attractions,@history,@t=1.0,[1.0,1.0],Array.new(6,0.0),0
    end
    def probability_a
      x=@lambda*(@attractions[1]-@attractions[0])
      1.0/(1.0+Math.exp(-[[x,-700.0].max,700.0].min))
    end
    def update(route_a:,payoff:,total_a:nil)
      raise ArgumentError,'route' unless [0,1].include?(route_a)
      obs=if @informed
        raise ArgumentError,'missing total_a' if total_a.nil?
        m=Integer(total_a)-route_a
        raise ArgumentError,'occupancy' unless (0..5).cover?(m)
        Array.new(6) { |j| j==m ? 1.0 : 0.0 }
      else
        RithmLearningModels.belief(route_a:route_a,payoff:payoff)
      end
      @t+=1
      @history=@history.each_index.map { |j| (@history[j]*(@t-1)+obs[j])/@t }
      surprise=(0..5).sum { |j| (@history[j]-obs[j])**2 }
      phi=1.0-0.5*surprise
      alt=if @informed
        RithmLearningModels.informed_counterfactual(route_a:route_a,payoff:payoff,total_a:total_a)
      else
        RithmLearningModels.inferred_counterfactual(route_a:route_a,payoff:payoff)
      end
      estimated=route_a==1 ? [alt,Float(payoff)] : [Float(payoff),alt]
      next_n=phi*@n+1.0
      @attractions=@attractions.each_index.map do |j|
        delta=estimated[j]>=Float(payoff)-1e-10 ? 1.0 : 0.0
        (phi*@n*@attractions[j]+delta*estimated[j])/next_n
      end
      @n=next_n
      {phi:phi,surprise:surprise,expected_others_a:obs.each_with_index.sum { |p,j| p*j },probability_a:probability_a}
    end
  end
  class SmallSample
    def initialize(informed:,max_sample:5,variable_sample:false,rng:Random.new(23))
      raise ArgumentError,'sample size' unless max_sample>=1
      @informed,@max_sample,@variable_sample,@rng=informed,max_sample,variable_sample,rng
      @payoffs=[[],[]]
    end
    def observe(route_a:,payoff:,total_a:nil)
      raise ArgumentError,'route' unless [0,1].include?(route_a)
      @payoffs[route_a]<<Float(payoff)
      if @informed
        raise ArgumentError,'missing total_a' if total_a.nil?
        @payoffs[1-route_a]<<RithmLearningModels.informed_counterfactual(route_a:route_a,payoff:payoff,total_a:total_a)
      end
    end
    def choose
      return @rng.rand(2) if @payoffs.any?(&:empty?)
      q=@variable_sample ? @rng.rand(1..@max_sample) : @max_sample
      means=@payoffs.map { |a| Array.new(q) { a[@rng.rand(a.size)] }.sum/q.to_f }
      return @rng.rand(2) if (means[0]-means[1]).abs<1e-12
      means[1]>means[0] ? 1 : 0
    end
  end
end
