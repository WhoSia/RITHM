# frozen_string_literal: true
require_relative 'r66_t17_oracle'
module RithmT17
  module Loop
    module_function
    BASE=RithmT16::Belief.binomial_base.map(&:to_f).freeze
    CLOCKS=[:common,:independent,:fixed_three].freeze
    # One fixed random tape per replication: same payoff shocks, disclosure uniforms,
    # eligibility uniforms and execution uniforms across counterfactual policies.
    def tape(seed,horizon)
      raise ArgumentError,'horizon' unless horizon.is_a?(Integer) && horizon>=1
      rng=Random.new(seed)
      Array.new(horizon-1) { [Array.new(6){rng.rand(10)},Array.new(6){rng.rand},Array.new(6){rng.rand},Array.new(6){rng.rand},rng.rand] }
    end
    def eligible(clock,us,shared)
      case clock
      when :common then Array.new(6,shared<0.5)
      when :independent then us.map { |u| u<0.5 }
      when :fixed_three
        chosen=(0...6).sort_by { |i| [us[i],i] }.first(3)
        (0...6).map { |i| chosen.include?(i) }
      else raise ArgumentError,'clock'
      end
    end
    def update(prior,route,payoff,k,disclosed,rho)
      if disclosed
        q=Array.new(6,0.0);q[k]=1.0
      else
        q=prior.each_with_index.map { |w,j| (6..16).cover?(payoff+(route ? j+1 : 2*(6-j))) ? w : 0.0 }
        z=q.sum;raise 'zero likelihood' unless z>0
        q.map! { |w| w/z }
      end
      q.each_with_index.map { |w,j| rho*w+(1-rho)*BASE[j] }
    end
    # Subjective reset model is not asserted to be the endogenous true transition.
    # Disclosure applies after current payoffs and before eligibility/next choice.
    # No future or unchosen private information enters the non-disclosed actor's decision.
    def run(n:,tape:,clock:,rho:,disclosure:,response:,threshold:0,memory: :filter)
      raise ArgumentError,'occupancy' unless n.is_a?(Integer) && n.between?(0,6)
      raise ArgumentError,'parameters' unless CLOCKS.include?(clock) && rho>=0 && rho<1 && [disclosure,response].all? { |x| x.between?(0,1) } && threshold>=0 && [:filter,:reset].include?(memory)
      routes=Array.new(6){ |i| i<n };beliefs=Array.new(6){BASE.dup};cost=3*(n-4)**2;switches=0;offers=0
      tape.each do |values,du,au,eu,shared|
        active=eligible(clock,au,shared);next_routes=routes.dup
        6.times do |i|
          a=routes[i];k=n-(a ? 1 : 0);y=6.5+values[i]-(a ? k+1 : 2*(6-k));seen=du[i]<disclosure
          offers+=1 if seen
          beliefs[i]=update(memory==:reset ? BASE : beliefs[i],a,y,k,seen,rho)
          gain=beliefs[i].each_with_index.sum { |p,j| p*(3*j-11) }*(a ? 1 : -1)
          if active[i] && gain>threshold+1e-12 && eu[i]<response
            next_routes[i]=!a;switches+=1
          end
        end
        routes=next_routes;n=routes.count(true);cost+=3*(n-4)**2
      end
      {cost:cost,switches:switches,offers:offers,final:n}
    end
  end
end
