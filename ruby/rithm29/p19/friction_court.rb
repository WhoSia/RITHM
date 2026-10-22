# frozen_string_literal: true
# RITHM-2.9 P19 — exact finite-game witness checker; NOT a global maximum solver.
module Rithm29P19
  PROGRAMS = %i[stop0 stop1 compute].freeze
  STATES = [[0,0],[0,1],[1,0],[1,1]].freeze
  Friction = Struct.new(:read_compute,:switching,:mismatch,keyword_init:true) do
    def validate!
      [read_compute,switching,mismatch].each do |v|
        raise ArgumentError, 'friction must be nonnegative Rational' unless v.is_a?(Rational) && v >= 0
      end
      self
    end
  end
  module_function
  def cost_matrix(state,friction)
    raise ArgumentError, 'unknown public state' unless STATES.include?(state)
    friction.validate!
    PROGRAMS.product(PROGRAMS).to_h do |a,b|
      value=[0.to_r,0.to_r]
      STATES.each do |x,y|
        parity=x^y
        acts=[a,b].map{|p|p==:compute ? parity : PROGRAMS.index(p)}
        [a,b].each_with_index do |prog,i|
          value[i]+=(acts.count(acts[i]).to_r +
            (acts[i]==parity ? 0 : friction.mismatch) +
            (prog==:compute ? friction.read_compute : 0) +
            (acts[i]==state[i] ? 0 : friction.switching))/4
        end
      end
      [[a,b],value]
    end
  end
  def validate_mix!(mix)
    raise ArgumentError, 'invalid mixed strategy' unless mix.size==3 && mix.all?{|z|z.is_a?(Rational)&&z>=0} && mix.sum==1
  end
  def verify(state,x,y,friction,future:nil)
    validate_mix!(x);validate_mix!(y)
    raise ArgumentError, 'future must cover all states and two players' if future && STATES.any?{|s|!future.key?(s)||future[s].size!=2||!future[s].all?{|v|v.is_a?(Rational)}}
    payoff=cost_matrix(state,friction)
    if future
      PROGRAMS.product(PROGRAMS).each do |a,b|
        expected=[0.to_r,0.to_r]
        STATES.each do |wx,wy|
          z=wx^wy
          route=[a,b].map{|p|p==:compute ? z : PROGRAMS.index(p)}
          next_value=future.fetch(route)
          2.times{|i|expected[i]+=next_value[i]/4}
        end
        2.times{|i|payoff[[a,b]][i]+=expected[i]}
      end
    end
    d0=PROGRAMS.map{|a|PROGRAMS.each_index.sum{|j|y[j]*payoff.fetch([a,PROGRAMS[j]])[0]}}
    d1=PROGRAMS.map{|b|PROGRAMS.each_index.sum{|i|x[i]*payoff.fetch([PROGRAMS[i],b])[1]}}
    v0=x.each_index.sum{|i|x[i]*d0[i]}
    v1=y.each_index.sum{|j|y[j]*d1[j]}
    {nash:d0.all?{|v|v>=v0}&&d1.all?{|v|v>=v1},values:[v0,v1],deviation_costs:[d0,d1]}
  end
  def stationary_witness(horizon)
    raise ArgumentError, 'horizon' unless horizon.is_a?(Integer)&&horizon>=1
    f=Friction.new(read_compute:1.to_r,switching:Rational(1,2),mismatch:2.to_r)
    policy={
      [0,0]=>[[Rational(3,4),Rational(1,4),0.to_r],[Rational(3,4),Rational(1,4),0.to_r]],
      [0,1]=>[[Rational(1,4),Rational(3,4),0.to_r],[Rational(3,4),Rational(1,4),0.to_r]],
      [1,0]=>[[Rational(3,4),Rational(1,4),0.to_r],[Rational(1,4),Rational(3,4),0.to_r]],
      [1,1]=>[[Rational(1,4),Rational(3,4),0.to_r],[Rational(1,4),Rational(3,4),0.to_r]]
    }
    STATES.each do |s|
      result=verify(s,*policy.fetch(s),f)
      raise 'invalid exact stage Nash witness' unless result[:nash]&&result[:values]==[Rational(11,4)]*2
    end
    {horizon:horizon,cost_by_player:Rational(11*horizon,4),social_cost:Rational(11*horizon,2),kind: :attained_lower_bound_only}
  end
end
