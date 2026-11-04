# frozen_string_literal: true
# P3-R8: falsify SSM plus a nonnegative common-freeze component.
# Observed moments and author-rule generative aggregates, not identified psychology.
require 'json'
require_relative 'activity_mixture'
module Rithm210SSMJointFalsifier
  module_function
  def compare(simulation:, observed:)
    [:early,:late].to_h do |epoch|
      base=simulation.fetch(epoch)
      real=observed.fetch(epoch)
      z=Rithm210ActivityMixture.freeze_required(
        base_zero:base.fetch(:zero),target_zero:real.fetch(:zero))
      result=if z.nil?
        {feasible:false,reason:'freeze-only cannot lower baseline no-switch probability',
         minimum_zero:base[:zero],observed_zero:real[:zero]}
      else
        current=real.fetch(:current_loss,0)
        next_loss=current+(1-z)*(base.fetch(:next_loss)-current)
        {feasible:true,freeze:z,predicted_next_loss:next_loss,
         observed_next_loss:real.fetch(:next_loss),
         welfare_error:next_loss-real.fetch(:next_loss)}
      end
      [epoch,result]
    end
  end
  def from_author_aggregate(path)
    sim=JSON.parse(File.read(path)).fetch('results').fetch('ssm5_3')
    [:early,:late].to_h do |epoch|
      row=sim.fetch(epoch.to_s)
      [epoch,{zero:row.fetch('no_switch_rate'),next_loss:row.fetch('next_loss')}]
    end
  end
end
if $PROGRAM_NAME==__FILE__
  sim=Rithm210SSMJointFalsifier.from_author_aggregate(ARGV.fetch(0))
  observed={early:{zero:34.0/154,next_loss:465.0/154},
            late:{zero:150.0/257,next_loss:342.0/257}}
  puts JSON.pretty_generate(Rithm210SSMJointFalsifier.compare(simulation:sim,observed:observed))
end
