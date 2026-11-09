# frozen_string_literal: true
# RITHM R23 prior-only actor memory and transition inertia, no participant data.
# A forecasting candidate combines exponential choice history with smoothed
# directional Markov transition counts. Group outcomes update AFTER prediction.
module Rithm210R23ActorMemory
  DECAYS=[0.5,0.8,1.0].freeze
  STRENGTHS=[2.0,5.0,12.0].freeze
  MIXES=[0.0,0.25,0.5,0.75,1.0].freeze
  class State
    attr_reader :periods
    def initialize
      @periods=0;@last=nil
      @freq=DECAYS.to_h{|d|[d,[0.0,0.0]]}
      @transitions={0=>[0,0],1=>[0,0]}
    end
    def frequency(decay)
      a,b=@freq.fetch(decay)
      (a+1.0)/(a+b+2.0)
    end
    def markov(strength)
      return 0.5 if @last.nil?
      switched,trials=@transitions.fetch(@last)
      p_switch=(switched+1.0)/(trials+strength)
      @last==1 ? 1.0-p_switch : p_switch
    end
    def update(choice)
      raise ArgumentError,'binary route required' unless [0,1].include?(choice)
      unless @last.nil?
        row=@transitions.fetch(@last)
        row[0]+=1 if @last!=choice
        row[1]+=1
      end
      @freq.each do |decay,(a,b)|
        @freq[decay]=[decay*a+choice,decay*b+1-choice]
      end
      @last=choice;@periods+=1
    end
  end
  module_function
  def candidates
    cases=DECAYS.map{|d|[d,5.0,0.0]}+STRENGTHS.map{|s|[1.0,s,1.0]}
    DECAYS.product(STRENGTHS,[0.25,0.5,0.75]).each{|cfg|cases<<cfg}
    cases.sort.freeze
  end
  def label(config)
    d,s,w=config
    return "frequency_decay_#{d}" if w==0.0
    return "markov_strength_#{s}" if w==1.0
    "memory_#{d}_markov_#{s}_mix_#{w}"
  end
  def forecast(actor,config)
    d,s,w=config
    p=(1-w)*actor.frequency(d)+w*actor.markov(s)
    raise 'invalid choice probability' unless p.finite?&&p.between?(0.0,1.0)
    p
  end
end
