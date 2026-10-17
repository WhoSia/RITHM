# frozen_string_literal: true
require 'json'
require 'openssl'

# Synthetic-only P1-P18 / prospective P2 composition probe.
# Two independently valid evidence bundles do not certify joint capacity.
module RithmCompositionCourt
  ROOTS = {'client-log' => 'PUBLIC-TEST-CLIENT-KEY', 'provider' => 'PUBLIC-TEST-PROVIDER-KEY'}.freeze
  FIELDS = %w[kind issuer person episode id parent occurred deadline demand].freeze
  module_function

  def mac(event)
    key = ROOTS.fetch(event.fetch('issuer'))
    canonical = FIELDS.map { |k| JSON.generate(event.fetch(k)) }.join('|')
    OpenSSL::HMAC.hexdigest('SHA256', key, canonical)
  end

  def signed(event)
    event.merge('mac' => mac(event))
  end

  def bundle(person:, episode:, deadline:, demand: 1)
    raise ArgumentError, 'positive deadline and demand required' unless deadline >= 1 && demand >= 1
    receipt = signed({'kind'=>'receipt','issuer'=>'client-log','person'=>person,'episode'=>episode,
      'id'=>"receipt:#{person}:#{episode}",'parent'=>'','occurred'=>0,'deadline'=>deadline,'demand'=>demand})
    commitment = signed({'kind'=>'service_commitment','issuer'=>'provider','person'=>person,'episode'=>episode,
      'id'=>"commit:#{person}:#{episode}",'parent'=>receipt.fetch('id'),'occurred'=>0,
      'deadline'=>deadline,'demand'=>demand})
    {'receipt'=>receipt,'commitment'=>commitment}
  end

  def validate!(b)
    r, c = b.fetch('receipt'), b.fetch('commitment')
    [[r,'receipt','client-log'],[c,'service_commitment','provider']].each do |ev, kind, issuer|
      raise 'typed issuer' unless ev.fetch('kind') == kind && ev.fetch('issuer') == issuer
      raise 'invalid MAC' unless ev.fetch('mac') == mac(ev)
      raise 'invalid chronology' unless ev.fetch('occurred') == 0 && ev.fetch('deadline') >= 1
      raise 'positive demand' unless ev.fetch('demand') >= 1
    end
    raise 'identity or episode mismatch' unless %w[person episode deadline demand].all? { |k| r.fetch(k) == c.fetch(k) }
    raise 'wrong parent' unless c.fetch('parent') == r.fetch('id') && r.fetch('parent') == ''
    raise 'duplicate record ID' if r.fetch('id') == c.fetch('id')
    true
  end

  # Exact finite-horizon dynamic program. Integer shared per-round capacity.
  # This is model completion only; real-world welfare_verified remains false.
  def synthesize(bundles, capacities:, boost_budget: 0)
    raise 'nonnegative capacities' unless capacities.all? { |v| v.is_a?(Integer) && v >= 0 }
    raise 'nonnegative boost budget' unless boost_budget.is_a?(Integer) && boost_budget >= 0
    bundles.each { |b| validate!(b) }
    jobs = bundles.map { |b| b.fetch('receipt') }
    keys = jobs.map { |j| [j.fetch('person'),j.fetch('episode')] }
    raise 'duplicate person-episode obligation' unless keys.uniq.length == keys.length
    horizon = capacities.size
    raise 'deadline outside horizon' if jobs.any? { |j| j.fetch('deadline') > horizon }
    memo = {}
    visit = nil
    visit = lambda do |t, remaining, spent|
      return remaining.all?(&:zero?) ? [] : nil if t == horizon
      key = [t, remaining, spent]
      return memo[key] if memo.key?(key)
      (0..(boost_budget-spent)).each do |boost|
        allocations = [[]]
        remaining.each do |r|
          allocations = allocations.flat_map { |prefix| (0..r).map { |a| prefix+[a] } }
        end
        allocations.each do |allocation|
          next if allocation.sum > capacities.fetch(t)+boost
          rem = remaining.each_index.map { |i| remaining[i] - allocation[i] }
          next if rem.each_index.any? { |i| rem[i]>0 && jobs[i].fetch('deadline') <= t+1 }
          suffix = visit.call(t+1,rem,spent+boost)
          return memo[key] = [[boost,allocation],*suffix] if suffix
        end
      end
      memo[key] = nil
    end
    solution = visit.call(0,jobs.map { |j| j.fetch('demand') },0)
    {'win'=>!solution.nil?, 'schedule'=>solution, 'states'=>memo.size,
      'synthetic_only'=>true, 'real_world_welfare_verified'=>false}
  end
end
