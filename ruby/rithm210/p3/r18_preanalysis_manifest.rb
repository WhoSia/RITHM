# frozen_string_literal: true
# R18-P5 local draft manifest fingerprint: does not constitute trial registration.
require 'json'
require 'digest'
module Rithm210R18PreanalysisManifest
  module_function
  PRIMARY='session_mean_sum_40_period_group_total_cost'.freeze
  def canonical(v)
    case v
    when Hash then v.keys.map(&:to_s).sort.to_h{|k|[k,canonical(v.fetch(k.to_sym){v.fetch(k)})]}
    when Array then v.map{|x|canonical(x)}
    else v
    end
  end
  def draft(design: :two_condition)
    raise ArgumentError,'unknown design' unless [:two_condition,:four_condition].include?(design)
    {version:'rithm-r18p5-v1',status:'unregistered_method_draft',
     unit:'independent_session',assignment:'session_level_once_before_40_rounds',
     design:design.to_s,conditions:design==:two_condition ?
       %w[current_frozen current_feedback] :
       %w[lagged_frozen lagged_feedback current_frozen current_feedback],
     primary:PRIMARY,horizon:40,participants_per_group:6,
     estimand:design==:two_condition ?
       'mean_feedback_minus_frozen_given_current_disclosure' :
       'mean_current_feedback_minus_current_frozen_minus_lagged_feedback_plus_lagged_frozen',
     baseline:'previous_and_current_true_occupancy_measured_before_allocation',
     manipulation:'truthful_timestamped_reports_and_one_turn_per_person',
     inferential_unit:'session',missing_outcome:'predefine_before_first_enrollment',
     caution:'Historical SD only a feasibility proxy, not prospective trial power'}
  end
  def validate(m)
    raise ArgumentError,'manifest must be map' unless m.is_a?(Hash)
    raise ArgumentError,'not a draft' unless m[:status]=='unregistered_method_draft'
    raise ArgumentError,'primary outcome changed' unless m[:primary]==PRIMARY
    raise ArgumentError,'horizon changed' unless m[:horizon]==40
    raise ArgumentError,'unit changed' unless m[:unit]=='independent_session'&&m[:inferential_unit]=='session'
    raise ArgumentError,'baseline invalid' unless m[:baseline]=='previous_and_current_true_occupancy_measured_before_allocation'
    raise ArgumentError,'missing outcomes not specified as pending' unless m[:missing_outcome]=='predefine_before_first_enrollment'
    true
  end
  def fingerprint(m)
    validate(m)
    Digest::SHA256.hexdigest(JSON.generate(canonical(m)))
  end
end
