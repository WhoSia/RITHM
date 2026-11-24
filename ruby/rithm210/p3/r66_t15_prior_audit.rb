# frozen_string_literal: true
require_relative 'r66_t14_decision'
module RithmT15
  module PriorAudit
    module_function
    # lambda = extra mass at n=4; remainder is uniform over seven occupancies.
    def values(route, concentration)
      l=Rational(concentration)
      raise ArgumentError,'concentration' unless l.between?(0,1)
      raise ArgumentError,'route' unless [:a,:b].include?(route)
      w=(0..6).map { |n| ((1-l)/7+(n==4 ? l : 0))*(route==:a ? n : 6-n) }
      p=w.map { |x| x/w.sum }
      g=(0..6).map { |n| RithmT14::Decision.gain(n,route) }
      net=p.zip(g).sum { |x,y| x*y }
      informed=p.zip(g).sum { |x,y| x*[y,0].max }
      {net:net, evsi:informed-[net,0].max}
    end
    def flip(n,route,concentration,costs=[0,2])
      v=values(route,concentration)
      g=RithmT14::Decision.gain(n,route)
      raise ArgumentError,'nonempty nonnegative costs' unless !costs.empty? && costs.all? { |x| x>=0 }
      Rational(costs.count { |c| v[:evsi]>c ? g>0 : v[:net]>0 },costs.length)
    end
    def equivalent?(concentration)
      (0..6).all? do |n|
        [:a,:b].all? do |route|
          # Exclude states in which the queried actor cannot be on the route.
          next true if (route==:a && n==0) || (route==:b && n==6)
          flip(n,route,concentration)==RithmT14::Decision.flip_probability(n,route,mechanism: :switching)
        end
      end
    end
  end
end
