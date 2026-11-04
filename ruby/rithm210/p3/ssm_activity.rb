# frozen_string_literal: true
# P3-R7 source-faithful generative SSM; separate state-conditioned diagnostics.
require_relative 'ssm_generative'
require 'json'
module Rithm210GenerativeSSMActivity
  module_function
  def run(replicates:10_000,seed:20261104)
    raise ArgumentError,'replicates' unless replicates.positive?
    rng=Random.new(seed)
    stats={}
    %i[ssm5 ssm1_9].each do |model|
      (1..3).each do |treatment|
        cells={early:{at4:0,no_switch:0,next_loss:0,gross:0,cancel:0},late:{at4:0,no_switch:0,next_loss:0,gross:0,cancel:0}}
        replicates.times do
          record=Rithm210GenerativeSSM.simulate_one(
            treatment:treatment,model:model,rng:rng,activity:true)[:activity]
          cells.each do |ep,a|
            record[ep].each{|k,v|a[k]+=v}
          end
        end
        stats["#{model}_#{treatment}"]=cells.transform_values do |c|
          raise 'no support' if c[:at4]==0
          {at4:c[:at4],no_switch:c[:no_switch],
            no_switch_rate:c[:no_switch].to_f/c[:at4],
            next_loss:c[:next_loss].to_f/c[:at4],
            mean_gross:c[:gross].to_f/c[:at4],
            cancellation_rate:c[:cancel].to_f/c[:at4]}
        end
      end
    end
    {replicates:replicates,seed:seed,
      scope:'free-running simulated groups, conditioned on simulated n_t=4',results:stats}
  end
end
puts JSON.pretty_generate(Rithm210GenerativeSSMActivity.run(
  replicates:Integer(ARGV.fetch(0,'10000')),
  seed:Integer(ARGV.fetch(1,'20261104')))) if $PROGRAM_NAME==__FILE__
