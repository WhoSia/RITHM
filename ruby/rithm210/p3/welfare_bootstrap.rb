# frozen_string_literal: true
# Paired 24-session bootstraps for downstream welfare forecast evaluation.
require 'json'
module Rithm210WelfareBootstrap
  module_function
  def run(input,draws:20_000,seed:20261104)
    rows=input.fetch('per_session'){input.fetch('by_session')}
    blocks=rows.sort_by{|s,_|s.to_i}.map do |s,vals|
      base=vals.fetch('baseline')
      v=->(name,key){vals.fetch(name).fetch(key)}
      {session:s.to_i,n:base.fetch('n'),
       logloss20:v.call('online_20','logloss')-v.call('baseline','logloss'),
       logloss80:v.call('online_80','logloss')-v.call('baseline','logloss'),
       mse20:v.call('online_20','mse')-v.call('baseline','mse'),
       mse80:v.call('online_80','mse')-v.call('baseline','mse')}
    end
    raise '24 session groups expected' unless
      blocks.size==24 && blocks.sum{|r|r[:n]}==5616
    [:logloss20,:logloss80,:mse20,:mse80].to_h do |metric|
      rng=Random.new(seed)
      mean=->(set){set.sum{|r|r[metric]*r[:n]}/set.sum{|r|r[:n]}.to_f}
      b=Array.new(draws) do
        mean.call(Array.new(blocks.size){blocks.fetch(rng.rand(blocks.size))})
      end.sort
      [metric,{point:mean.call(blocks),lower:b[(draws*0.025).floor],
        upper:b[(draws*0.975).floor],
        sessions_improved:blocks.count{|r|r[metric]<0}}]
    end
  end
end
if __FILE__==$PROGRAM_NAME
  input=JSON.parse(File.read(ARGV.fetch(0)))
  puts JSON.pretty_generate(Rithm210WelfareBootstrap.run(input,
    draws:Integer(ARGV.fetch(1,'20000'))))
end
