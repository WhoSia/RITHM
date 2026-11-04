# frozen_string_literal: true
# Exploratory sample-size sensitivity. NOT a replication of original Table 7.
require_relative 'ssm_generative'
require 'json'
module Rithm210SSMSampleSizeSensitivity
  module_function
  def run(q_values:[1,2,3,5,9,15,30],replicates:1000,seed:20261104)
    raise ArgumentError,'replicates' unless replicates>0
    rng=Random.new(seed)
    rows=q_values.to_h do |q|
      cells={early:{at4:0,no_switch:0,next_loss:0},late:{at4:0,no_switch:0,next_loss:0}}
      replicates.times do
        sim=Rithm210GenerativeSSM.simulate_one(
          treatment:3,model: :ssm5,rng:rng,activity:true,fixed_q:q)
        cells.each do |ep,a|
          sim[:activity][ep].each{|k,v|a[k]+=v}
        end
      end
      [q,cells.transform_values do |a|
        {at4:a[:at4],no_switch_rate:a[:no_switch].to_f/a[:at4],
          next_loss:a[:next_loss].to_f/a[:at4]}
      end]
    end
    {seed:seed,replicates:replicates,full_q_sensitivity:rows}
  end
end
puts JSON.pretty_generate(Rithm210SSMSampleSizeSensitivity.run(
  replicates:Integer(ARGV.fetch(0,'1000')))) if __FILE__==$PROGRAM_NAME
