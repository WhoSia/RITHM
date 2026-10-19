# frozen_string_literal: true
require_relative 'dynamic_court'
require 'json'
r=Rithm29DynamicCourt.run(horizon:3)
states=r.fetch(:policies).map do |(t,prev),x|
 {Previous:prev,Remaining:t,Chosen:x[:selected][:programs].map{|p|p==:stop ? 0 : 1},
  Equilibria:x[:equilibrium_count],Costs:x[:selected][:costs].map(&:to_s)}
end.sort_by{|x|[x[:Remaining],x[:Previous]]}
puts JSON.generate({Horizon:3,Initial:r[:expected_costs].map(&:to_s),States:states})
