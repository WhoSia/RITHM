# frozen_string_literal: true
# Audit within-session treatment order; do not presume randomized assignment.
require_relative 'treatment_epoch_cv'
module Rithm210SectionOrderAudit
  module_function
  def report(path)
    summarize(Rithm210TreatmentEpochCV.predict(Rithm210ResidualNegativeControl.read_groups(path)))
  end
  def summarize(rows)
    mapping=rows.group_by{|r|[r[:session],r[:section]]}.map do |(s,section),a|
      treatments=a.map{|r|r[:treatment]}.uniq
      raise 'section contains multiple treatments' unless treatments.size==1
      {session:s,section:section,treatment:treatments.first,n:a.size}
    end
    per_session=mapping.group_by{|r|r[:session]}
    raise 'treatment design mismatch' unless per_session.size==24 &&
      per_session.values.all?{|a|a.size==3 && a.map{|r|r[:treatment]}.sort==[1,2,3]}
    distribution=mapping.group_by{|r|[r[:section],r[:treatment]]}.map do |(sec,trt),a|
      {section:sec,treatment:trt,sessions:a.size}
    end.sort_by{|r|[r[:section],r[:treatment]]}
    losses=rows.group_by{|r|[r[:section],r[:treatment]]}.map do |(sec,trt),a|
      {section:sec,treatment:trt,n:a.size,
        joint_delta:a.sum{|r|r[:joint1]-r[:joint0]}/a.size.to_f}
    end.sort_by{|r|[r[:section],r[:treatment]]}
    {sessions:24,treatment_sequence_counts:per_session.values.map{|a|
      a.sort_by{|r|r[:section]}.map{|r|r[:treatment]}.join('-')}.tally,
      assignment_counts:distribution,section_treatment_losses:losses}
  end
end
puts JSON.pretty_generate(Rithm210SectionOrderAudit.report(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
