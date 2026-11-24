# frozen_string_literal: true
# Subjective common occupancy prior; exact one-shot myopic decision.
module RithmT14
  module Decision
    module_function
    STATES = (0..6).freeze
    def prior
      STATES.map { |n| Rational(1,140)+(n==4 ? Rational(19,20) : 0) }
    end
    def gain(n, route)
      raise ArgumentError, 'occupancy' unless STATES.include?(n)
      case route
      when :a then 3*n-14
      when :b then 11-3*n
      else raise ArgumentError, 'route'
      end
    end
    def posterior(route)
      raise ArgumentError, 'route' unless [:a,:b].include?(route)
      w=prior.each_with_index.map { |p,n| p*(route==:a ? n : 6-n) }
      w.map { |x| x/w.sum }
    end
    def values(route, threshold:0)
      k=Rational(threshold)
      raise ArgumentError, 'threshold' if k.negative?
      p=posterior(route)
      e=p.each_with_index.sum(Rational(0)) { |w,n| w*(gain(n,route)-k) }
      informed=p.each_with_index.sum(Rational(0)) { |w,n| w*[gain(n,route)-k,0].max }
      {uninformed:[e,0].max, informed:informed, net_prior_gain:e, value_of_information:informed-[e,0].max}
    end
    # Two equally likely freshly drawn private types, independent across actors and dates.
    # Cognitive type: cost 0 or 2 to observe n. Switching-cost type: full n, cost 0 or 12 to switch.
    # Free information and threshold removal are different interventions, not real welfare fees.
    def flip_probability(n,route,mechanism:,policy: :baseline, disclosure:1)
      reveal=Rational(disclosure)
      raise ArgumentError, 'disclosure in [0,1]' unless reveal.between?(0,1)
      raise ArgumentError, 'policy' unless [:baseline,:free_info,:remove_threshold].include?(policy)
      g=gain(n,route)
      case mechanism
      when :cognitive
        v=values(route)
        base=Rational([0,2].count { |c| v[:value_of_information]>c ? g>0 : v[:net_prior_gain]>0 },2)
        policy==:free_info ? (1-reveal)*base+reveal*(g>0 ? 1 : 0) : base
      when :switching
        costs=policy==:remove_threshold ? [0,0] : [0,12]
        Rational(costs.count { |c| g>c },2)
      else raise ArgumentError, 'mechanism'
      end
    end
  end
end
