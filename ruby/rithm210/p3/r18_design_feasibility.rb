# frozen_string_literal: true
# R18-P4: prospective cluster count examples, no participant trial.
module Rithm210R18DesignFeasibility
  module_function
  HISTORICAL_SD=29.58918598975362
  ZSUM=1.959963984540054+0.8416212335729143
  def clusters_each(sd:,effect:,contrast: :feedback)
    raise ArgumentError,'finite positive inputs' unless [sd,effect].all?{|x|x.is_a?(Numeric)&&x.finite?&&x>0}
    factor={feedback:2,interaction:4}.fetch(contrast){raise ArgumentError,'contrast'}
    [2,(factor*ZSUM**2*(sd/effect)**2).ceil].max
  end
  def compare(effect:20,sd:HISTORICAL_SD)
    feedback=clusters_each(sd:sd,effect:effect,contrast: :feedback)
    interaction=clusters_each(sd:sd,effect:effect,contrast: :interaction)
    {feedback:{per_condition:feedback,total:2*feedback},
     interaction:{per_condition:interaction,total:4*interaction},
     warning:'Not equal estimands. Historical variance only; nominal Gaussian approximation, not actual trial power.'}
  end
end
