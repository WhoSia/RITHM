# frozen_string_literal: true
require_relative 'epoch_conditioned_model'
module Rithm210EpochBootstrap
  module_function
  def run(rows,draws:20_000,seed:20261103)
    [:joint,:count,:cross].to_h do |head|
      n=rows.size; rng=Random.new(seed)
      mean=->(rr){rr.sum{|r|r[:n]*r.fetch(head)}/rr.sum{|r|r[:n]}.to_f}
      boot=Array.new(draws) do
        draw=Array.new(n){rows.fetch(rng.rand(n))}
        mean.call(draw)
      end.sort
      [head,{mean:mean.call(rows),lower:boot[(draws*0.025).floor],
        upper:boot[(draws*0.975).floor],improved_sessions:rows.count{|r|r.fetch(head)<0}}]
    end
  end
end
if __FILE__==$PROGRAM_NAME
  r=Rithm210EpochConditionedModel.run(ARGV.fetch(0))
  puts JSON.pretty_generate({summary:r.reject{|k,_|k==:session_delta},
    bootstrap:Rithm210EpochBootstrap.run(r[:session_delta])})
end
