# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'dynamic'
class TestRevocableObservation < Minitest::Test
  M=RithmDynamic
  def cfg(h:5,budget:1,cost:0,delay:1,revoke:6,restore:6)
    {'horizon'=>h,'budget'=>budget,'probe_cost'=>cost,'delay'=>delay,
     'revoke_at'=>revoke,'restore_at'=>restore}
  end
  def wins(c)
    M.synthesize(c).fetch('certificate_type')=='winning'
  end
  def test_five_round_exact_budget_pairs
    assert wins(cfg(budget:1))
    refute wins(cfg(budget:0))
    refute wins(cfg(budget:1,revoke:0))
    assert wins(cfg(budget:2,revoke:0))
  end
  def test_six_round_exact_budget_pairs
    assert wins(cfg(h:6,budget:0,revoke:7,restore:7))
    refute wins(cfg(h:6,budget:0,revoke:0,restore:7))
    assert wins(cfg(h:6,budget:1,revoke:0,restore:7))
  end
  def test_restoration_deadline_example
    assert wins(cfg(revoke:0,restore:4))
    refute wins(cfg(revoke:0,restore:5))
    assert wins(cfg(revoke:0,restore:5,budget:2))
  end
  def test_price_and_latency_effect
    assert wins(cfg(cost:0,budget:1,delay:1))
    refute wins(cfg(cost:1,budget:1,delay:1))
    refute wins(cfg(cost:0,budget:1,delay:5))
  end
  def test_synthetic_claim_fence
    cert=M.synthesize(cfg)
    assert_equal true,cert.fetch('synthetic_only')
    assert_equal false,cert.fetch('real_world_welfare_verified')
    assert_equal M::SCHEMA,cert.fetch('schema')
    assert_equal M.key(M.root(cfg)),cert.fetch('root')
  end
  def test_revocation_masks_delayed_observation
    c=cfg(revoke:0,restore:3)
    first=M.outcomes(c,M.root(c),[0,0,1])
    assert_equal [2],first.map(&:first)
    assert_equal false,M.trust_at(c,2)
    assert_equal true,M.trust_at(c,3)
  end
  def test_bad_contract_rejected
    assert_raises(ArgumentError){M.synthesize(cfg(delay:0))}
    assert_raises(ArgumentError){M.synthesize(cfg(revoke:2,restore:1))}
    assert_raises(ArgumentError){M.synthesize(cfg(budget:5))}
  end
end
