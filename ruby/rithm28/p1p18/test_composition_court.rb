# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'composition_court'

class TestRithmCompositionCourt < Minitest::Test
  C = RithmCompositionCourt
  def a; C.bundle(person:'A',episode:'E1',deadline:1); end
  def b(deadline:1); C.bundle(person:'B',episode:'E1',deadline:deadline); end

  def test_individually_valid_but_joint_capacity_fails
    assert C.validate!(a)
    assert C.validate!(b)
    assert C.synthesize([a],capacities:[1])['win']
    assert C.synthesize([b],capacities:[1])['win']
    refute C.synthesize([a,b],capacities:[1])['win']
  end
  def test_increased_capacity_restores_feasibility
    s=C.synthesize([a,b],capacities:[2])
    assert s['win']
    assert_equal 2,s['schedule'][0][1].sum
  end
  def test_later_deadline_restores_feasibility
    s=C.synthesize([a,b(deadline:2)],capacities:[1,1])
    assert s['win']
    assert_equal 2,s['schedule'].sum { |round| round[1].sum }
  end
  def test_outage_causes_compositional_failure
    refute C.synthesize([a,b(deadline:2)],capacities:[1,0])['win']
  end
  def test_one_capacity_repair_restores_guarantee
    s=C.synthesize([a,b(deadline:2)],capacities:[1,0],boost_budget:1)
    assert s['win']
    assert_equal 1,s['schedule'].sum { |round| round[0] }
  end
  def test_duplicate_person_episode_rejected
    assert_raises(RuntimeError) { C.synthesize([a,a],capacities:[2]) }
  end
  def test_cross_subject_rejected_even_with_correct_test_mac
    forged=Marshal.load(Marshal.dump(a))
    forged['commitment']['person']='B'
    forged['commitment']['mac']=C.mac(forged['commitment'])
    assert_raises(RuntimeError) { C.validate!(forged) }
  end
  def test_wrong_parent_rejected_even_with_correct_test_mac
    forged=Marshal.load(Marshal.dump(a))
    forged['commitment']['parent']='unrelated'
    forged['commitment']['mac']=C.mac(forged['commitment'])
    assert_raises(RuntimeError) { C.validate!(forged) }
  end
  def test_wrong_issuer_and_unsigned_mutation_rejected
    forged=Marshal.load(Marshal.dump(a))
    forged['commitment']['issuer']='client-log'
    forged['commitment']['mac']=C.mac(forged['commitment'])
    assert_raises(RuntimeError) { C.validate!(forged) }
    forged2=Marshal.load(Marshal.dump(a))
    forged2['receipt']['demand']=5
    assert_raises(RuntimeError) { C.validate!(forged2) }
  end
  def test_recovery_not_real_world_attestation
    s=C.synthesize([a],capacities:[1])
    assert_equal false,s['real_world_welfare_verified']
    assert_equal true,s['synthetic_only']
  end
end
