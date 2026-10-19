# frozen_string_literal: true
require 'json'
# Finite-state metareasoning court; no behavioral or empirical identification.
# Probe is an optional perfect unilateral-gain computation costing q_i.
# Agent probes and switches iff unilateral gain exceeds q_i + k_i.
module RithmDeliberationCourt
  module_function
  def cost(routes)
    raise ArgumentError, 'three binary routes' unless routes.size == 3 && routes.all? { |r| [0,1].include?(r) }
    n=routes.count(0)
    n*n+(3-n)*(3-n)
  end
  def gain(routes,i)
    own=routes.count(routes.fetch(i))
    own-(4-own) # latency before - latency after a unilateral move
  end
  def update(routes,q:,k:,schedule: :parallel)
    raise ArgumentError unless q.size==3 && k.size==3 && (q+k).all?{|c| c.is_a?(Integer)&&c>=0}
    raise ArgumentError unless [:parallel,:sequential].include?(schedule)
    next_routes=routes.dup
    probes=Array.new(3,false)
    3.times do |i|
      local=schedule==:parallel ? routes : next_routes
      # Strict expected gain: no free speculative probe of non-improving alternatives.
      if gain(local,i)>q[i]+k[i]
        probes[i]=true
        next_routes[i]=1-local[i]
      end
    end
    {'routes'=>next_routes,'probed'=>probes,'social_cost'=>cost(next_routes),
      'deliberation_spend'=>probes.each_index.sum{|i| probes[i] ? q[i] : 0},
      'switch_spend'=>probes.each_index.sum{|i| probes[i] ? k[i] : 0}}
  end
  def simulate(initial:,q:,k:,horizon:4,schedule: :parallel)
    raise ArgumentError unless (1..12).cover?(horizon)
    s=initial.dup; states=[s]; stages=[]
    horizon.times do
      r=update(s,q:q,k:k,schedule:schedule)
      stages<<r
      s=r.fetch('routes')
      states<<s
    end
    {'states'=>states,'costs'=>states.map{|v|cost(v)},
      'deliberation_total'=>stages.sum{|r|r.fetch('deliberation_spend')},
      'switching_total'=>stages.sum{|r|r.fetch('switch_spend')},
      'stages'=>stages,'source'=>'synthetic only'}
  end
  def exhaustive(horizon:4)
    states=(0...8).map{|m|3.times.map{|i|(m>>i)&1}}
    vectors=(0...27).map{|m|3.times.map{|i|(m/(3**i))%3}}
    checked=0;violations=0;witness=nil
    vectors.each do |q|
      vectors.each do |k|
        states.each do |initial|
          [:parallel,:sequential].each do |schedule|
            outcome=simulate(initial:initial,q:q,k:k,horizon:horizon,schedule:schedule)
            checked+=1
            if outcome.fetch('states').any?{|s|s.size!=3}
              violations+=1
            end
            witness||=outcome if initial==[0,0,0] && q==[0,0,0] && k==[0,0,0] && schedule==:parallel
          end
        end
      end
    end
    {'checked'=>checked,'violations'=>violations,
     'witness'=>{'states'=>witness.fetch('states'),'costs'=>witness.fetch('costs')},
     'boundary'=>'from AAA a player acts iff q_i+k_i<2',
     'caveat'=>'myopic deterministic oracle; the probe decision presumes its unilateral gain; this is NOT genuine costly discovery'}
  end
end
if __FILE__==$PROGRAM_NAME
  puts JSON.pretty_generate(RithmDeliberationCourt.exhaustive)
end
