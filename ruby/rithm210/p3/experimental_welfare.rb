# frozen_string_literal: true
# Exact welfare transform for the ACTUAL six-actor Noussair-Qiao experiment.
# Chosen A cost = n_A; chosen B cost = 2*(6-n_A).
# All expected values can use Rational; never equate forecast logloss with welfare.
module Rithm210ExperimentalWelfare
  module_function

  def cost(n)
    raise ArgumentError,'n must be an integer from 0 to 6' unless n.is_a?(Integer) && n.between?(0,6)
    n*n+2*(6-n)*(6-n)
  end

  def excess(n)
    cost(n)-24
  end

  def expected_excess(current_a:,joint:)
    raise ArgumentError,'bad current occupancy' unless current_a.is_a?(Integer) && current_a.between?(0,6)
    raise ArgumentError,'joint distribution empty' if joint.empty?
    mass=joint.values.sum
    raise ArgumentError,'not normalized' unless (mass-1).abs<1e-10
    moments={e_u:0,e_d:0,e_u2:0,e_d2:0,e_ud:0}
    direct=0
    joint.each do |(up,down),p|
      raise ArgumentError,'invalid turnover' unless up.is_a?(Integer) && down.is_a?(Integer) &&
        up.between?(0,6-current_a) && down.between?(0,current_a)
      raise ArgumentError,'invalid mass' if p<0
      next_a=current_a+up-down
      direct+=p*excess(next_a)
      moments[:e_u]+=up*p;moments[:e_d]+=down*p
      moments[:e_u2]+=up*up*p;moments[:e_d2]+=down*down*p
      moments[:e_ud]+=up*down*p
    end
    mu=current_a+moments[:e_u]-moments[:e_d]
    v_u=moments[:e_u2]-moments[:e_u]**2
    v_d=moments[:e_d2]-moments[:e_d]**2
    cov=moments[:e_ud]-moments[:e_u]*moments[:e_d]
    from_moments=3*((mu-4)**2+v_u+v_d-2*cov)
    raise 'welfare identity failed' unless (direct-from_moments).abs<1e-10
    {expected_excess:direct,mean_next_a:mu,var_up:v_u,var_down:v_d,
     covariance_up_down:cov,identity_value:from_moments}
  end

  def coupling_examples
    h=Rational(1,2);q=Rational(1,4)
    positive={[0,0]=>h,[1,1]=>h}
    independent={[0,0]=>q,[0,1]=>q,[1,0]=>q,[1,1]=>q}
    negative={[0,1]=>h,[1,0]=>h}
    {positive:positive,independent:independent,negative:negative}.transform_values do |dist|
      expected_excess(current_a:4,joint:dist)
    end
  end
end
