# frozen_string_literal: true
require 'csv'
require 'json'
module Rithm210ResidualNegativeControl
  module_function
  def key(r)
    [r.fetch('trt').to_i, r.fetch('Informed').to_i, r.fetch('RouteA').to_i, r.fetch('Cost').to_f]
  end
  def read_groups(path)
    result = Hash.new { |h,k| h[k] = [] }
    CSV.foreach(path, headers: true) do |r|
      s = r.fetch('session').to_i
      t = r.fetch('trt').to_i
      p = r.fetch('Period').to_i
      next unless t.between?(1,3) && s != 2 && s != 101 && p.between?(1,39)
      result[[s,r.fetch('section').to_i,r.fetch('Group').to_i,p]] << r
    end
    raise 'wrong groups' unless result.size == 5616 && result.values.all? { |g| g.size == 6 }
    result
  end
  def fit(groups, folds, fold)
    local = Hash.new { |h,k| h[k] = [0,0] }
    global = Hash.new { |h,k| h[k] = [0,0] }
    groups.each do |group_key, members|
      s = group_key[0]
      next if folds.fetch(s) == fold
      members.each do |r|
        y = r.fetch('switchWill').to_i
        raise 'bad switch flag' unless y.between?(0,1)
        x = local[key(r)]; x[0] += y; x[1] += 1
        z = global[r.fetch('RouteA').to_i]; z[0] += y; z[1] += 1
      end
    end
    [local,global]
  end
  def probability(model,r,alpha: 20.0)
    local,global = model
    k = local.fetch(key(r),[0,0]); b = global.fetch(r.fetch('RouteA').to_i,[0,0])
    prior = (b[0] + 1.0) / (b[1] + 2.0)
    (k[0]+alpha*prior)/(k[1]+alpha)
  end
  def bootstrap(rows, metric, draws: 20_000, seed: 20261103)
    sessions = rows.map { |r| r.fetch(:session) }.uniq.sort
    blocks = sessions.map do |s|
      sample = rows.select { |r| r[:session] == s }
      [sample.sum { |r| r.fetch(metric) }, sample.size]
    end
    point = blocks.sum(&:first) / blocks.sum(&:last).to_f
    rng = Random.new(seed)
    boot = Array.new(draws) do
      selection = Array.new(blocks.size) { blocks.fetch(rng.rand(blocks.size)) }
      selection.sum(&:first) / selection.sum(&:last).to_f
    end.sort
    {mean:point,lower:boot[(draws*0.025).floor],upper:boot[(draws*0.975).floor]}
  end
  def run(path, draws: 20_000)
    groups = read_groups(path)
    sessions = groups.keys.map(&:first).uniq.sort
    raise 'wrong sessions' unless sessions.size == 24
    folds = sessions.each_with_index.to_h { |s,i| [s,i%6] }
    records = []
    6.times do |fold|
      model = fit(groups,folds,fold)
      groups.each do |(s, section, g, period), members|
        next unless folds.fetch(s) == fold
        a = members.select { |r| r['RouteA'].to_i == 1 }
        b = members.select { |r| r['RouteA'].to_i == 0 }
        eu = b.sum { |r| probability(model,r) }
        ed = a.sum { |r| probability(model,r) }
        u = members.sum { |r| r['switchBtoAWill'].to_i }
        d = members.sum { |r| r['switchAtoBWill'].to_i }
        vu = b.sum { |r| p=probability(model,r); p*(1-p) }
        vd = a.sum { |r| p=probability(model,r); p*(1-p) }
        records << {session:s,section:section,group:g,period:period,
          treatment:members.first.fetch('trt').to_i,
          ru:u-eu,rd:d-ed,cross:(u-eu)*(d-ed),variance_null:vu*vd}
      end
    end
    raise 'wrong scored groups' unless records.size==5616
    # Same period/section, different group: deliberately imperfect negative control.
    by_time = records.group_by { |r| [r[:session],r[:section],r[:period]] }
    other = []
    matched_difference = []
    by_time.each_value do |sub|
      next if sub.size < 2
      sub.each do |r|
        neighbors = sub.reject { |q| q[:group] == r[:group] }
        next if neighbors.empty?
        control = r[:ru]*neighbors.sum { |q| q[:rd] }/neighbors.size.to_f
        other << {session:r[:session], cross:control}
        matched_difference << {session:r[:session], difference:r[:cross]-control}
      end
    end
    strata = records.group_by { |r| r[:treatment] }.to_h do |t,rs|
      [t, {n:rs.size,within:bootstrap(rs,:cross,draws:draws),
        u_bias:bootstrap(rs,:ru,draws:draws),d_bias:bootstrap(rs,:rd,draws:draws)}]
    end
    {n_groups:records.size,sessions:sessions.size,
      within:bootstrap(records,:cross,draws:draws),
      expected_null_variance:records.sum { |r| r[:variance_null] }/records.size.to_f,
      cross_group_negative_control:{n:other.size,score:bootstrap(other,:cross,draws:draws)},
      matched_within_minus_between:{n:matched_difference.size,score:bootstrap(matched_difference,:difference,draws:draws)},
      by_treatment:strata}
  end
end
if __FILE__ == $PROGRAM_NAME
  puts JSON.pretty_generate(Rithm210ResidualNegativeControl.run(ARGV.fetch(0), draws:Integer(ARGV.fetch(1,'20000'))))
end
