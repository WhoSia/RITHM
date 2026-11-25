# frozen_string_literal: true
# Full state disclosure, own current eligibility known BEFORE decision, previous eligibility remembered.
# Conditional prediction of others' next choices; no future or other actors' private eligibility.
module RithmT22
  module Context
    BASE=[1,10,40,80,80,32].map { |v| v/243.0 }.freeze
    CLOCKS=[:common,:independent,:fixed_three].freeze
    MODES=[:fixed,:pooled,:conditional].freeze
    class Rows
      def initialize(mode,strength:4.0,rho:0.45)
        raise ArgumentError,'mode/parameters' unless MODES.include?(mode) && strength>0 && rho>=0 && rho<1
        @mode=mode;@prior=(0..5).map { |k| BASE.each_with_index.map { |b,j| strength*(rho*(k==j ? 1 : 0)+(1-rho)*b) } }
        @counts=Array.new(2){Array.new(6){Array.new(6,0)}};@last=nil
      end
      def context(active); @mode==:conditional && active ? 1 : 0;end
      def observe(k,active)
        raise ArgumentError,'state/eligibility' unless k.is_a?(Integer) && k.between?(0,5) && [true,false].include?(active)
        if @last && @mode!=:fixed
          old,c=@last;@counts[c][old][k]+=1
        end
        c=context(active);@last=[k,c]
        w=@prior[k].zip(@counts[c][k]).map { |p,x| p+x };z=w.sum
        w.map { |v| v/z }
      end
    end
    module_function
    def tape(seed,horizon)
      rng=Random.new(seed);Array.new(horizon-1){[Array.new(6){rng.rand},Array.new(6){rng.rand},rng.rand]}
    end
    def eligibility(clock,us,shared)
      case clock
      when :common then Array.new(6,shared<0.5)
      when :independent then us.map { |u| u<0.5 }
      when :fixed_three then ids=(0...6).sort_by { |i| [us[i],i] }.first(3); (0...6).map { |i| ids.include?(i) }
      else raise ArgumentError,'clock'
      end
    end
    def run(tape:,clock:,response:,mode:,n:5,strength:4.0)
      raise ArgumentError,'parameters' unless n.is_a?(Integer) && n.between?(0,6) && response.between?(0,1)
      fs=Array.new(6){Rows.new(mode,strength:strength)};routes=Array.new(6){|i| i<n};cost=3*(n-4)**2;paths=[];switches=0
      tape.each do |us,eu,shared|
        active=eligibility(clock,us,shared);ks=routes.map { |a| n-(a ? 1 : 0) };paths<<[ks,active];next_routes=routes.dup
        6.times do |i|
          p=fs[i].observe(ks[i],active[i]);g=p.each_with_index.sum { |v,k| v*(3*k-11) }*(routes[i] ? 1 : -1)
          if active[i] && g>1e-12 && eu[i]<response
            next_routes[i]=!routes[i];switches+=1
          end
        end
        routes=next_routes;n=routes.count(true);cost+=3*(n-4)**2
      end
      paths<<[routes.map { |a| n-(a ? 1 : 0) },Array.new(6,false)] # terminal outcome only
      {cost:cost,switches:switches,paths:paths}
    end
    # Match realized paths; evaluate only transitions FROM eligible decision periods.
    def replay(paths,strength:4.0)
      MODES.to_h do |mode|
        fs=Array.new(6){Rows.new(mode,strength:strength)};s=0.0;cnt=0
        paths.each_cons(2) do |(ks,active),(next_ks,_)|
          6.times do |i|
            p=fs[i].observe(ks[i],active[i]);next unless active[i]
            s-=Math.log(p[next_ks[i]]);cnt+=1
          end
        end
        [mode,[s,cnt]]
      end
    end
  end
end
