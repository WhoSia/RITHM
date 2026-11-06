# frozen_string_literal: true
# R21: nested session-heldout EWA-added-value comparison.
require_relative 'r21_ewa_group_cv'

module Rithm210R21EWAIncrementalCV
  module_function

  def choose(rows, training_sessions, treatment)
    candidates = rows.select { |r| r.fetch(:treatment) == treatment && training_sessions.include?(r.fetch(:session)) }
    grouped = candidates.group_by { |r| r.fetch(:variant) }
    raise 'no models' if grouped.empty?
    grouped.min_by do |name, items|
      session_rows = items.group_by { |r| r.fetch(:session) }
      raise 'unequal training support' unless session_rows.keys.sort == training_sessions.sort &&
                                           session_rows.values.all? { |rs| rs.size == 1 }
      [items.sum { |r| r.fetch(:logloss) } / items.size, name]
    end.first
  end

  def run(path, candidates: Rithm210R21EWAGroupCV.grid, weights: [0.0, 0.5, 1.0])
    raise ArgumentError, 'weights require distinct zero and 0..1' unless
      weights.is_a?(Array) && weights.uniq == weights && weights.include?(0.0) &&
      weights.all? { |w| w.is_a?(Numeric) && w.finite? && w.between?(0, 1) }
    groups = Rithm210R21EWAGroupCV.source(path)
    sessions = groups.keys.map(&:first).uniq.sort
    raise '24 sessions required' unless sessions.size == 24
    scores = []
    candidates.each_with_index do |p, i|
      weights.each do |weight|
        next if weight.zero? && i > 0
        label = weight.zero? ? 'own_route_frequency' : "ewa_#{p.label}_w#{weight}"
        predicted = Rithm210R21EWAGroupCV.predict_scores(groups, p, blend: weight)
        predicted.group_by { |r| [r[:session], r[:treatment]] }.each do |(s, trt), rs|
          scores << {session: s, treatment: trt, variant: label,
                     **Rithm210R20GroupBridge.summary(rs)}
        end
      end
    end
    folds = sessions.each_with_index.to_h { |s, i| [s, i % 6] }
    heldout = []
    6.times do |fold|
      test = sessions.select { |s| folds.fetch(s) == fold }
      train = sessions - test
      (1..3).each do |trt|
        winner = choose(scores, train, trt)
        scores.each do |r|
          heldout << r.merge(fold: fold) if test.include?(r[:session]) &&
                                           r[:treatment] == trt && r[:variant] == winner
        end
      end
    end
    raise 'heldout session coverage' unless heldout.size == 72
    models = heldout.group_by { |r| r[:treatment] }.to_h do |trt, rs|
      [trt, {sessions: rs.size, groups: rs.sum { |r| r[:groups] },
             logloss: rs.sum { |r| r[:logloss] } / rs.size.to_f,
             brier: rs.sum { |r| r[:brier] } / rs.size.to_f,
             cost_abs_error: rs.sum { |r| r[:cost_abs_error] } / rs.size.to_f,
             selected: rs.group_by { |r| r[:variant] }.transform_values(&:size)}]
    end
    {sessions: 24, models: models, variants: scores.map { |r| r[:variant] }.uniq.size,
     session_results: heldout,
     caveat: 'Session-equal-weight exploratory selection. Historical groups have unequal sizes per session; differs from pooled R20 scores. No heldout independent source.'}
  end
end

puts JSON.pretty_generate(Rithm210R21EWAIncrementalCV.run(ARGV.fetch(0))) if __FILE__ == $PROGRAM_NAME
