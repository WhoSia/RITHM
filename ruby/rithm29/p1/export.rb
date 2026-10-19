# frozen_string_literal: true
require_relative 'dynamic_court'
require 'json'
def rat_text(x)
 x.denominator==1 ? x.numerator.to_s : x.to_s
end
r=Rithm29DynamicCourt.run(horizon:3)
states=r.fetch(:policies).map do |(t,prev),x|
 {Previous:prev,Remaining:t,Chosen:x[:selected][:programs].map{|p|p==:stop ? 0 : 1},
  Equilibria:x[:equilibrium_count],Costs:x[:selected][:costs].map{|n|rat_text(n)}}
end.sort_by{|x|[x[:Remaining],x[:Previous]]}
puts JSON.generate({Horizon:3,Initial:r[:expected_costs].map(&:to_s),States:states})
