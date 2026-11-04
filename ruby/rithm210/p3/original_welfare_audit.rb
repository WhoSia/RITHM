# frozen_string_literal: true
# Original human-source welfare audit. No person-level rows are written to stdout.
require 'csv'
require 'digest'
require 'json'

module Rithm210OriginalWelfareAudit
  module_function
  def epoch(period)
    return 'early' if period <= 10
    return 'late' if period >= 30
    'middle'
  end
  def read_groups(path,expected_groups:5616)
    result={}
    CSV.foreach(path,headers:true) do |r|
      s=r['session'].to_i
      trt=r['trt'].to_i
      period=r['Period'].to_i
      next unless trt.between?(1,3) && s!=2 && s!=101 && period.between?(1,39)
      n=r['NumA'].to_i
      chosen_cost=r['RouteA'].to_i==1 ? n : 2*(6-n)
      raise 'individual routing cost mismatch' unless r['Cost'].to_i==chosen_cost
      raise 'observed profit != value-cost' unless
        (r['profit'].to_f-(r['Value'].to_f-r['Cost'].to_f)).abs<1e-9
      key=[s,r['section'].to_i,r['Group'].to_i,period]
      rec=result[key]||={session:s,section:key[1],group:key[2],period:period,
        treatment:trt,epoch:epoch(period),n:n,next_n:r['NumAnext'].to_i,
        cost:0,persons:0,up:0,down:0,ids:[]}
      raise 'group label mismatch' unless rec[:n]==n &&
        rec[:next_n]==r['NumAnext'].to_i && rec[:treatment]==trt
      rec[:cost]+=r['Cost'].to_i
      rec[:persons]+=1
      rec[:up]+=r['switchBtoAWill'].to_i
      rec[:down]+=r['switchAtoBWill'].to_i
      rec[:ids]<<r['ID'].to_i
    end
    raise "wrong group count #{result.size}" unless result.size==expected_groups
    result.each_value do |g|
      raise 'group participants mismatch' unless g[:persons]==6 && g[:ids].uniq.size==6
      raise 'welfare polynomial mismatch' unless g[:cost]==24+3*(g[:n]-4)**2
      raise 'future count mismatch' unless g[:next_n]==g[:n]+g[:up]-g[:down]
      g[:excess]=g[:cost]-24
    end
    result.values
  end
  def paired_session_bootstrap(rows,draws:20_000,seed:20261104)
    by=rows.group_by{|r|r[:session]}
    raise 'must have 24 sessions' unless by.size==24
    summaries=by.keys.sort.map do |session|
      a=by.fetch(session).group_by{|x|[x[:treatment],x[:epoch]]}
      raise 'missing treatment-period' unless
        (1..3).all?{|t|%w[early late].all?{|e|a[[t,e]]&.any?}}
      avg=->(trt,ep){v=a.fetch([trt,ep]);v.sum{|g|g[:excess]}/v.size.to_f}
      {session:session,full_early:avg.call(3,'early'),full_late:avg.call(3,'late'),
        no_early:avg.call(1,'early'),no_late:avg.call(1,'late')}
    end
    transform=->(r){(r[:full_early]-r[:full_late])-(r[:no_early]-r[:no_late])}
    point=summaries.sum{|r|transform.call(r)}/summaries.size.to_f
    rng=Random.new(seed)
    boot=Array.new(draws) do
      sample=Array.new(summaries.size){summaries.fetch(rng.rand(summaries.size))}
      sample.sum{|r|transform.call(r)}/sample.size.to_f
    end.sort
    {estimand:'equal-session Full vs No early-to-late excess-cost contrast',
      point:point,lower:boot[(draws*0.025).floor],
      upper:boot[(draws*0.975).floor],session_count:summaries.size,draws:draws}
  end
  def run(path,draws:20_000)
    rows=read_groups(path)
    strata=rows.group_by{|r|[r[:treatment],r[:epoch]]}.map do |(t,e),a|
      mu=a.sum{|r|r[:n]}/a.size.to_f
      variance=a.sum{|r|(r[:n]-mu)**2}/a.size.to_f
      bias_component=3*(mu-4)**2
      dispersion_component=3*variance
      excess=a.sum{|r|r[:excess]}/a.size.to_f
      raise 'mean-variance welfare identity mismatch' unless
        (excess-bias_component-dispersion_component).abs<1e-9
      {treatment:t,epoch:e,n:a.size,mean_num_a:mu,
        variance_num_a:variance,mean_bias_loss:bias_component,
        dispersion_loss:dispersion_component,
        mean_excess:excess,
        mean_cost:a.sum{|r|r[:cost]}/a.size.to_f}
    end.sort_by{|x|[x[:treatment],x[:epoch]]}
    {sha256:Digest::SHA256.file(path).hexdigest,
      groups:rows.size,sessions:rows.map{|r|r[:session]}.uniq.size,
      persons:rows.sum{|r|r[:persons]},original_cost_identity_verified:true,
      group_occupancy_histogram:rows.group_by{|r|r[:n]}.transform_values(&:size),
      group_mean_excess:rows.sum{|r|r[:excess]}/rows.size.to_f,
      strata:strata,paired_session_contrast:paired_session_bootstrap(rows,draws:draws)}
  end
end
if __FILE__==$PROGRAM_NAME
  puts JSON.pretty_generate(Rithm210OriginalWelfareAudit.run(ARGV.fetch(0),
    draws:Integer(ARGV.fetch(1,'20000'))))
end
