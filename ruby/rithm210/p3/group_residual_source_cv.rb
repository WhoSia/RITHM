# frozen_string_literal: true
# P3-R13: heldout actor probabilities -> exact welfare-error terms.
# Only prints aggregates; SHA sealed participant CSV stays in Drive.
require_relative '../p2/online_actor_history'
require_relative 'activity_event_cv'
require_relative 'group_residual_welfare'
require 'digest'
require 'json'
module Rithm210GroupResidualSourceCV
  module_function

  def source_rows(csv)
    raise 'original CSV SHA mismatch' unless Digest::SHA256.file(csv).hexdigest == Rithm210ActivityEventCV::SHA
    groups = Rithm210OnlineIdentity.source(csv)
    sessions = groups.keys.map(&:first).uniq.sort
    raise 'unexpected session count' unless sessions.size == 24
    folds = sessions.each_with_index.to_h { |s,i| [s,i % 6] }
    rows = []
    6.times do |fold|
      held = sessions.select { |s| folds[s] == fold }
      fitted = Rithm210OnlineIdentity.train(groups,held)
      history = Hash.new { |h,k| h[k] = [0,0] }
      keys = groups.keys.select { |k| held.include?(k[0]) }.sort_by { |s,section,g,t| [s,section,t,g] }
      keys.each do |s,section,g,t|
        people = groups.fetch([s,section,g,t])
        base = people.map { |p| Rithm210OnlineIdentity.probability(fitted,p) }
        models = {baseline: base}
        [20,80].each do |strength|
          models["online_#{strength}".to_sym] = people.each_with_index.map do |p,i|
            Rithm210OnlineIdentity.online_probability(base[i],history[[s,section,p['ID'].to_i]],strength.to_f)
          end
        end
        if people.first['trt'].to_i == 3 && people.first['NumA'].to_i == 4 && (t <= 10 || t >= 30)
          routes = people.map { |p| p['RouteA'].to_i }
          switches = people.map { |p| p['switchWill'].to_i }
          u = people.sum { |p| p['switchBtoAWill'].to_i }
          d = people.sum { |p| p['switchAtoBWill'].to_i }
          raise 'source switch mismatch' unless switches.sum == u+d
          raise 'source occupancy mismatch' unless 4+u-d == people.first['NumAnext'].to_i
          models.each do |name,probs|
            result = Rithm210GroupResidualWelfare.analyze(routes,switches,probs)
            rows << {session:s,model:name,epoch:t<=10 ? :early : :late,metrics:result}
          end
        end
        # Update actor's own information only AFTER the period-t prediction.
        people.each do |p|
          h = history[[s,section,p['ID'].to_i]]
          h[0] += p['switchWill'].to_i
          h[1] += 1
        end
      end
    end
    raise 'selected 411 groups x 3 models required' unless rows.size == 1233
    [sessions,rows]
  end

  def summary(rows)
    Rithm210GroupResidualWelfare.aggregate(rows.map { |r| r.fetch(:metrics) })
  end

  def bootstrap(sessions, rows, draws:20_000, seed:20261105)
    raise ArgumentError, 'positive draws required' unless draws.positive?
    buckets = rows.group_by { |r| [r[:model],r[:epoch]] }
    rng = Random.new(seed)
    point = buckets.to_h { |key,rs| [key.join('_'),summary(rs)] }
    keys = [:welfare_error,:linear_calibration,:diagonal_calibration,:same_route_pair,:opposite_route_pair]
    ci = {}
    buckets.each do |key,rs|
      per_session = rs.group_by { |r| r[:session] }
      draws_by_key = keys.to_h { |k| [k,[]] }
      draws.times do
        selected = Array.new(sessions.size) { sessions.fetch(rng.rand(sessions.size)) }
        sample = selected.flat_map { |s| per_session.fetch(s,[]) }
        next if sample.empty?
        x = summary(sample)
        keys.each { |k| draws_by_key[k] << x[k] }
      end
      ci[key.join('_')] = draws_by_key.to_h do |k,values|
        v=values.sort
        [k,[v[(v.size*0.025).floor],v[(v.size*0.975).floor]]]
      end
    end
    {sessions:sessions.size,selected_groups:rows.size/3,draws:draws,seed:seed,
     point:point,conditional_session_bootstrap95:ci,
     caveat:'same-source exploratory; selected nA4; conditional on fitted CV models; no causal or dependence identification'}
  end

  def run(csv,draws:20_000,seed:20261105)
    sessions,rows = source_rows(csv)
    bootstrap(sessions,rows,draws:draws,seed:seed)
  end
end
puts JSON.pretty_generate(Rithm210GroupResidualSourceCV.run(ARGV.fetch(0),draws:Integer(ARGV.fetch(1,'20000')))) if __FILE__ == $PROGRAM_NAME
