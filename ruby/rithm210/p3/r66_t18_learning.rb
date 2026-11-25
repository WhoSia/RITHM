# frozen_string_literal: true
# R66-T18: subjective persistence learning, synthetic six-actor feedback only.
module RithmT18
  BASE = [1,10,40,80,80,32].map { |x| x / 243.0 }.freeze
  CLOCKS = [:common,:independent,:fixed_three].freeze
  module_function

  # joint prior over (rho,K). No actual K enters a private update unless disclosed.
  class Filter
    attr_reader :grid, :joint
    def initialize(grid)
      raise ArgumentError,'grid' unless !grid.empty? && grid.all? { |r| r>=0 && r<1 }
      @grid=grid.freeze
      @joint=grid.map { BASE.map { |p| p/grid.size } }
    end
    def marginal
      (0..5).map { |k| @joint.sum { |row| row[k] } }
    end
    def mean_rho
      @joint.each_with_index.sum { |row,i| row.sum*@grid[i] }
    end
    def observe(route,payoff,disclosed_k:nil,forget:0.0)
      raise ArgumentError,'route/forget' unless [:a,:b].include?(route) && forget.between?(0,1)
      raise ArgumentError,'disclosed state' unless disclosed_k.nil? || (0..5).include?(disclosed_k)
      w=@joint.map do |row|
        row.each_with_index.map do |p,k|
          compatible=(6..16).cover?(payoff+(route==:a ? k+1 : 2*(6-k)))
          compatible && (disclosed_k.nil? || k==disclosed_k) ? p : 0.0
        end
      end
      mass=w.sum(&:sum); raise 'zero likelihood' unless mass>0
      w.each { |row| row.map! { |p| p/mass } }
      pred=w.each_with_index.map do |row,i|
        r=@grid[i]; m=row.sum
        row.each_with_index.map { |p,k| r*p+(1-r)*m*BASE[k] }
      end
      # Discount rho knowledge while retaining the marginal state forecast.
      # This is a phenomenological forgetting operator, not optimal costly learning.
      if forget>0
        m=(0..5).map { |k| pred.sum { |row| row[k] } }
        pred.each { |row| row.each_index { |k| row[k]=(1-forget)*row[k]+forget*m[k]/@grid.size } }
      end
      @joint=pred
      gain=marginal.each_with_index.sum { |p,k| p*(3*k-11) }
      route==:a ? gain : -gain
    end
  end

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
  def run(n:,tape:,clock:,grid:,disclosure:,response:,threshold:0,forget:0.0)
    raise ArgumentError,'parameters' unless n.is_a?(Integer) && n.between?(0,6) && [disclosure,response,forget].all? { |x| x.between?(0,1) } && threshold>=0
    routes=Array.new(6){ |i| i<n }; filters=Array.new(6){Filter.new(grid.dup)}
    cost=3*(n-4)**2; switches=0; loss=0.0; first_exit=nil; n0=n
    tape.each_with_index do |(values,du,au,eu,shared),t|
      active=eligible(clock,au,shared); next_routes=routes.dup
      6.times do |i|
        a=routes[i]; k=n-(a ? 1 : 0); y=6.5+values[i]-(a ? k+1 : 2*(6-k))
        # Evaluator-only score of pre-observation prediction; never fed into filter.
        loss-=Math.log(filters[i].marginal[k]) if t>0
        gain=filters[i].observe(a ? :a : :b,y,disclosed_k:du[i]<disclosure ? k : nil,forget:forget)
        if active[i] && gain>threshold+1e-12 && eu[i]<response
          next_routes[i]=!a; switches+=1
        end
      end
      routes=next_routes;n=routes.count(true);cost+=3*(n-4)**2
      first_exit||=t+1 if n!=n0
    end
    {cost:cost,switches:switches,final:n,first_exit:first_exit,rho:filters.sum(&:mean_rho)/6,logloss:tape.size>1 ? loss/(6*(tape.size-1)) : nil}
  end

  # Exact posterior odds after m identical observed transitions, two-point rho prior.
  def repeated_odds(k:,m:,low:Rational(1,5),high:Rational(4,5))
    raise ArgumentError,'state/count/grid' unless (0..5).include?(k) && m.is_a?(Integer) && m>=0 && 0<=low && low<high && high<1
    b=Rational([1,10,40,80,80,32][k],243)
    ((high+(1-high)*b)/(low+(1-low)*b))**m
  end
end
