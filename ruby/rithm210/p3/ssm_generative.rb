# frozen_string_literal: true
# Independent self-generated SSM simulations. Appendix B Table 12.
# Rule-level replication; original RNG stream / original source unavailable.
require 'json'
module Rithm210GenerativeSSM
  module_function
  def choose(hist,informed:,q:,rng:)
    return rng.rand(2) if hist[:a].empty? && hist[:b].empty?
    if informed
      h=hist[:pair]
      raise 'informed history missing' if h.empty?
      advantage=0.0
      q.times { advantage += h[rng.rand(h.length)] }
    else
      a=hist[:a]; b=hist[:b]
      return rng.rand(2) if a.empty? || b.empty?
      advantage=0.0
      q.times {advantage += a[rng.rand(a.length)] - b[rng.rand(b.length)]}
    end
    return 1 if advantage>0
    return 0 if advantage<0
    rng.rand(2)
  end
  def simulate_one(treatment:,model:,rng:,periods:40,activity:false,fixed_q:nil)
    raise ArgumentError,'treatment' unless (1..3).cover?(treatment)
    raise ArgumentError,'model' unless %i[ssm5 ssm1_9].include?(model)
    informed=case treatment
      when 1 then Array.new(6,false)
      when 2 then Array.new(3,true)+Array.new(3,false)
      when 3 then Array.new(6,true)
    end
    raise ArgumentError,'fixed_q only for SSM5' if fixed_q && model!=:ssm5
    raise ArgumentError,'fixed_q positive integer' if fixed_q && (!fixed_q.is_a?(Integer) || fixed_q<1)
    # SSM1-9 assigns one q_i to each individual for the entire 40-period game.
    sizes=Array.new(6){ model==:ssm5 ? (fixed_q || 5) : rng.rand(1..9) }
    histories=Array.new(6){{a:[],b:[],pair:[]}}
    cost=[];count=[]
    actions_last=nil
    n_last=nil
    activity_stats={early:{at4:0,no_switch:0,next_loss:0},late:{at4:0,no_switch:0,next_loss:0}}
    periods.times do |index|
      actions=Array.new(6){|i|choose(histories[i],informed:informed[i],q:sizes[i],rng:rng)}
      n=actions.sum
      cost << ((n*n+2*(6-n)**2)/6.0)
      count << n
      if activity && index>0 && n_last==4
        previous_period=index
        epoch=previous_period<=10 ? :early : previous_period>=30 ? :late : nil
        if epoch
          cell=activity_stats[epoch]
          cell[:at4]+=1
          cell[:no_switch]+=1 if actions==actions_last
          cell[:next_loss]+=3*(n-4)**2
        end
      end
      actions_last=actions
      n_last=n
      6.times do |i|
        value=6.0+10.0*rng.rand
        n_other=n-actions[i]
        a_profit=value-(n_other+1)
        b_profit=value-2*(6-n_other)
        histories[i][:pair] << (a_profit-b_profit) if informed[i]
        histories[i][actions[i]==1 ? :a : :b] << (actions[i]==1 ? a_profit : b_profit)
      end
    end
    metrics={cost_early:cost.first(10).sum/10.0,
     cost_late:cost.last(10).sum/10.0,
     a_early:count.first(10).sum/10.0,
     a_late:count.last(10).sum/10.0,
     cost_all:cost.sum/periods.to_f,
     a_all:count.sum/periods.to_f}
    activity ? metrics.merge(activity:activity_stats) : metrics
  end
  def run(replicates:10_000,seed:20261104)
    raise ArgumentError,'replicates positive' unless replicates.positive?
    rng=Random.new(seed)
    data={}
    %i[ssm5 ssm1_9].each do |model|
      (1..3).each do |treatment|
        rows=Array.new(replicates){simulate_one(treatment:treatment,model:model,rng:rng)}
        stats=rows.first.keys.to_h do |key|
          mean=rows.sum{|r|r[key]}/replicates.to_f
          var=rows.sum{|r|(r[key]-mean)**2}/replicates.to_f
          [key,{mean:mean,sd:Math.sqrt(var)}]
        end
        data["#{model}_#{treatment}"]=stats
      end
    end
    {seed:seed,replicates:replicates,
      interpretation:'independent free-running SSM40, not the authors original random stream',
      results:data}
  end
end
puts JSON.pretty_generate(Rithm210GenerativeSSM.run(
  replicates:Integer(ARGV.fetch(0,'10000')),
  seed:Integer(ARGV.fetch(1,'20261104')))) if $PROGRAM_NAME==__FILE__
