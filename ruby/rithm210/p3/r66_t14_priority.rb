# frozen_string_literal: true
# Scores are revisable judgments, NOT estimated probabilities or statistical confidence.
module RithmT14
  module Priority
    module_function
    L_WEIGHTS={b:Rational(25,100),d:Rational(25,100),w:Rational(20,100),f:Rational(15,100),r:Rational(15,100)}.freeze
    E_WEIGHTS={direct:Rational(30,100),independent:Rational(20,100),reproducible:Rational(20,100),falsification:Rational(20,100),scope:Rational(10,100)}.freeze
    GATES=[:ready,:prepare,:blocked,:done].freeze
    def weighted(values,weights)
      raise ArgumentError,'missing or extra axes' unless values.keys.sort==weights.keys.sort
      weights.sum(Rational(0)) do |axis,weight|
        v=Rational(values.fetch(axis))
        raise ArgumentError,'axis must be in [0,1]' unless v.between?(0,1)
        v*weight
      end
    end
    def rank(tasks)
      raise ArgumentError,'duplicate IDs' unless tasks.map { |t| t.fetch(:id) }.uniq.length==tasks.length
      tasks.map do |t|
        gate=t.fetch(:gate)
        raise ArgumentError,'invalid gate' unless GATES.include?(gate)
        t.merge(l:weighted(t.fetch(:axes),L_WEIGHTS),eligible:gate==:ready)
      end.sort_by { |t| [t[:eligible] ? 0 : 1,-t[:l],t[:id]] }
    end
    def evidence(axes:,claim:,generalization:)
      c=Rational(claim);g=Rational(generalization)
      raise ArgumentError,'claim/generalization must be in [0,1]' unless [c,g].all? { |x| x.between?(0,1) }
      {e:weighted(axes,E_WEIGHTS),c:c,g:g}
    end
  end
end
