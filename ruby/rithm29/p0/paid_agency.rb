# frozen_string_literal: true
require 'json'
# RITHM-2.9 P0: explicit paid finite instruction program in a two-agent game.
# Hidden bits X,Y are fresh fair bits; parity is the preferred service/resource.
# Two policies only: STOP => route 0; COMPUTE => READ_X,READ_Y,XOR,route parity.
# Restricted instruction language; no claim about universal computational hardness.
module Rithm29PaidAgency
  module_function
  POLICIES = [:stop, :compute].freeze
  WORLDS = [[0,0],[0,1],[1,0],[1,1]].freeze
  def execute(program, world, read_fee:, xor_fee:)
    raise ArgumentError, 'unknown program' unless POLICIES.include?(program)
    return {route: 0, instructions: [:stop], computation_cost: 0} if program == :stop
    x,y=world
    {route: x^y, instructions: [:read_x,:read_y,:xor,:act],
     computation_cost: 2*read_fee+xor_fee}
  end
  def outcome(programs,world,read_fee:,xor_fee:,mismatch_loss:)
    traces=programs.map{|p|execute(p,world,read_fee:read_fee,xor_fee:xor_fee)}
    routes=traces.map{|t|t.fetch(:route)}
    parity=world[0]^world[1]
    losses=traces.each_with_index.map{|t,i|
      routes.count(routes[i]) + (routes[i]==parity ? 0 : mismatch_loss) + t.fetch(:computation_cost)}
    {routes:routes,individual:losses,social:losses.sum,traces:traces}
  end
  def expected(programs,read_fee:Rational(1,4),xor_fee:Rational(1,2),mismatch_loss:2)
    raise ArgumentError unless programs.size==2 && programs.all?{|p|POLICIES.include?(p)}
    raise ArgumentError unless read_fee>=0&&xor_fee>=0&&mismatch_loss>=0
    results=WORLDS.map{|w|outcome(programs,w,read_fee:read_fee,xor_fee:xor_fee,mismatch_loss:mismatch_loss)}
    {individual:2.times.map{|i|results.sum{|x|x[:individual][i]}/4},
     social:results.sum{|x|x[:social]}/4}
  end
  def audit(read_fee:Rational(1,4),xor_fee:Rational(1,2),mismatch_loss:2)
    ps=POLICIES.product(POLICIES)
    rows=ps.map do |pair|
      value=expected(pair,read_fee:read_fee,xor_fee:xor_fee,mismatch_loss:mismatch_loss)
      deviations=2.times.map{|i|
        other=pair.dup; other[i]=(pair[i]==:stop ? :compute : :stop)
        expected(other,read_fee:read_fee,xor_fee:xor_fee,mismatch_loss:mismatch_loss)[:individual][i]-value[:individual][i]}
      {policies:pair,individual:value[:individual],social:value[:social],deviations:deviations,
       pure_nash:deviations.all?{|x|x>=0}}
    end
    # In the symmetric mixed game each player computes independently with probability x.
    # Difference own expected COMPUTE - STOP = (fee - mismatch_loss/2 - 1/2) + x.
    fee=2*read_fee+xor_fee
    x=Rational(mismatch_loss,2)+Rational(1,2)-fee
    mixed=nil
    if x.between?(0,1)
      welfare=(1-x)**2*rows[0][:social] +
        x*(1-x)*(rows[1][:social]+rows[2][:social])+x*x*rows[3][:social]
      mixed={probability_compute:x,social:welfare,
        off_support_check: (x==0 || x==1 ? 'boundary-only' : 'full two-action support')}
    end
    {rows:rows,pure_equilibria:rows.select{|a|a[:pure_nash]},symmetric_mixed:mixed,
     world_count:4,instruction_language:[:read_x,:read_y,:xor,:stop,:act],
     agent_count:2,actual_computation_charged:true,external_human_validation:false}
  end
end
