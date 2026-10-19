# frozen_string_literal: true
require 'json'
# Restricted finite algorithm language: registers are initially unknown.
# READ_X and READ_Y cost q each; XOR is a separately priced computation c.
# Only XOR fills the output register used by final choice. STOP can choose a
# constant output when output register is blank. This is a declared ISA, not
# a universal lower bound; an unrestricted lookup could avoid paid XOR.
module RithmFiniteProcedure
  module_function
  def solve(read_fee:,xor_fee:,wrong_loss:4)
    raise ArgumentError unless [read_fee,xor_fee,wrong_loss].all?{|x|x.is_a?(Rational)||x.is_a?(Integer)} &&
      read_fee>=0 && xor_fee>=0 && wrong_loss>0
    # Worlds 00 01 10 11 equiprobable. Cost of fixed action 0 or 1 is L/2.
    stop=Rational(wrong_loss,2)
    # A single READ cannot improve parity prediction with unknown independent bit.
    one_probe=read_fee+stop
    full=2*read_fee+xor_fee
    act=full<stop ? 'READ_X;READ_Y;XOR;ACT' : 'STOP;ACT_CONSTANT'
    {'stop_expected_cost'=>stop,'one_probe_then_stop_cost'=>one_probe,
     'two_reads_and_compute_cost'=>full,'optimal_policy'=>act,
     'two_step_benefit'=>stop-full,'one_step_improvement'=>stop-one_probe,
     'states'=>4,'agent_memory'=>'three one-bit registers (x,y,output) + instruction pointer',
     'restricted_instruction_set'=>true,
     'physical_cognitive_cost_calibrated'=>false}
  end
end
if __FILE__==$PROGRAM_NAME
 puts JSON.pretty_generate(RithmFiniteProcedure.solve(read_fee:Rational(1,4),xor_fee:Rational(1,2)))
end
