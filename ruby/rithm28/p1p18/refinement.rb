# frozen_string_literal: true
require_relative 'dynamic'

# Finite-model refinement court: information may be ignored at zero probe price.
# This tests a logical inclusion, not a human behavioral welfare result.
module RithmRefinement
  module_function
  def decision(c)
    RithmDynamic.synthesize(c).fetch('certificate_type') == 'winning'
  end
  def compare(base, stronger)
    RithmDynamic.validate!(base)
    RithmDynamic.validate!(stronger)
    fixed=%w[horizon budget probe_cost delay]
    raise ArgumentError, 'different physical resource contract' unless fixed.all?{|k|base.fetch(k)==stronger.fetch(k)}
    raise ArgumentError, 'nonzero information price' unless base.fetch('probe_cost')==0
    h=base.fetch('horizon')
    (1..h).each do |t|
      weaker=RithmDynamic.trust_at(base,t)
      stronger_valid=RithmDynamic.trust_at(stronger,t)
      raise ArgumentError, 'not a trust-channel refinement' if weaker && !stronger_valid
    end
    low=decision(base)
    high=decision(stronger)
    {'weaker_wins'=>low,'stronger_wins'=>high,'inclusion_maintained'=>!low||high,
     'claim'=>'finite model only; controller can ignore free information'}
  end
end
