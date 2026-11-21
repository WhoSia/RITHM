# frozen_string_literal: true
require_relative 'r66_t12_kernel'
module RithmT12
  module PairwiseIdentity
    module_function
    # Exact one-step welfare difference given symmetric actor schedules.
    # Does not extend without conditions to 40-period policy welfare.
    def direct_one_step(schedule,n,effort:Rational(1))
      p,_=Kernel.transition(schedule,effort)
      p[n].each_with_index.sum(Rational(0)) { |pr,j| pr*Kernel.route_cost(j) }
    end
    def pairwise_factor(n,effort=Rational(1))
      a,b=Kernel.revision_rates(n)
      a*=Rational(effort);b*=Rational(effort)
      Schedules.choose(n,2)*a*a+Schedules.choose(6-n,2)*b*b-n*(6-n)*a*b
    end
    def symmetric_joints(schedule)
      joints=(0...6).flat_map { |a| ((a+1)...6).map { |b| Schedules.pair_joint(schedule,a,b) } }
      raise ArgumentError,'schedule must be exchangeable' unless joints.uniq.length == 1
      joints.fetch(0)
    end
    def expected_gap(n,first,second,effort:Rational(1))
      a=Schedules.validate(first);b=Schedules.validate(second)
      6.times do |i|
        raise ArgumentError,'unequal actor marginal' unless Schedules.marginal(a,i)==Schedules.marginal(b,i)
      end
      6*(symmetric_joints(a)-symmetric_joints(b))*pairwise_factor(n,effort)
    end
  end
end
