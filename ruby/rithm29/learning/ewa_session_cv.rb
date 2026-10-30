# frozen_string_literal: true
# Source-faithful one-step-ahead EWA-lite CV, independent of Python implementation.
# Usage: ruby ewa_session_cv.rb /path/to/data_task_all_switch_230705.csv
require 'csv'
require 'json'
require_relative 'learning_models'
raw = CSV.foreach(ARGV.fetch(0), headers: true).select do |r|
  r['trt'].to_i <= 3 && ![2, 101].include?(r['session'].to_i) && r['section'].to_i <= 4
end
raise 'bad sample size' unless raw.size == 34_560
persons = raw.group_by { |r| [r['trt'], r['session'], r['section'], r['Group'], r['ID']] }
obs = []
persons.each do |_key, rows|
  rows.sort_by! { |r| r['Period'].to_i }
  raise 'missing periods' unless rows.map { |r| r['Period'].to_i } == (1..40).to_a
  inf = rows.first['Informed'].to_i == 1
  m = RithmLearningModels::EWA.new(informed: inf, lambda: 1.0)
  previous = nil
  rows.each do |r|
    pa = m.probability_a
    obs << {session: r['session'].to_i, trt: r['trt'].to_i,
            informed: r['Informed'].to_i, y: r['RouteA'].to_i,
            previous_route: previous, diff: Math.log(pa / (1.0 - pa))}
    previous = r['RouteA'].to_i
    m.update(route_a: previous, payoff: r['profit'].to_f,
             total_a: inf ? r['NumA'].to_i : nil)
  end
end
# Same whole-session folds as sklearn GroupKFold with 24 sessions.
folds = [[7,105,108,110], [8,104,109,111], [4,10,103,112],
         [3,9,102,113], [5,106,115,117], [6,107,114,116]]
raise 'session overlap' unless folds.flatten.sort == obs.map { |o| o[:session] }.uniq.sort
def crossentropy(y, p)
  p = [[p, 1e-12].max, 1 - 1e-12].min
  y == 1 ? -Math.log(p) : -Math.log(1 - p)
end
def fit_lambda(train)
  objective = lambda do |x|
    train.sum do |o|
      z = (2 * o[:y] - 1) * x * o[:diff]
      Math.log(1 + Math.exp(-z.abs)) + [-z, 0.0].max
    end / train.size
  end
  a,b=0.0,16.0;rho=(Math.sqrt(5.0)-1)/2
  c=b-rho*(b-a);d=a+rho*(b-a);fc=objective.call(c);fd=objective.call(d)
  40.times do
    if fc <= fd
      b,d,fd=d,c,fc;c=b-rho*(b-a);fc=objective.call(c)
    else
      a,c,fc=c,d,fd;d=a+rho*(b-a);fd=objective.call(d)
    end
  end
  (a+b)/2
end
scores = Hash.new { |h,k| h[k]={ll:0.0,brier:0.0,correct:0,n:0} }
parameters = []
folds.each do |held|
  train=obs.reject { |o| held.include?(o[:session]) }
  test=obs.select { |o| held.include?(o[:session]) }
  estimate=fit_lambda(train)
  parameters << estimate
  counts = Hash.new { |h,k| h[k]=[0,0] }
  transitions = Hash.new { |h,k| h[k]=[0,0] }
  train.each do |o|
    key = [o[:trt],o[:informed]]
    counts[key][0] += o[:y];counts[key][1] += 1
    unless o[:previous_route].nil?
      t=transitions[key+[o[:previous_route]]];t[0]+=o[:y];t[1]+=1
    end
  end
  test.each do |o|
    key = [o[:trt],o[:informed]]
    pos,n = counts[key]
    base = (pos+1).fdiv(n+2)
    markov = if o[:previous_route].nil?
      base
    else
      pos2,n2=transitions[key+[o[:previous_route]]]
      (pos2+2).fdiv(n2+4)
    end
    pewa = 1.0 / (1.0 + Math.exp(-estimate * o[:diff]))
    {'ewa'=>pewa, 'markov'=>markov}.each do |model,p|
      v=scores[model]
      v[:ll]+=crossentropy(o[:y],p)
      v[:brier]+=(o[:y]-p)**2
      v[:correct]+=((p>=0.5)==(o[:y]==1) ? 1 : 0)
      v[:n]+=1
    end
  end
end
summary=scores.transform_values { |v| {logloss:v[:ll]/v[:n],brier:v[:brier]/v[:n],accuracy:v[:correct].fdiv(v[:n]),n:v[:n]} }
puts JSON.pretty_generate({lambda_folds:parameters,models:summary})
