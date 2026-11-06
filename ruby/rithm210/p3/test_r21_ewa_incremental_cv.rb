require 'minitest/autorun'
require_relative 'r21_ewa_incremental_cv'

class TestRithm210R21EWAIncrementalCV < Minitest::Test
  M = Rithm210R21EWAIncrementalCV

  def fixture
    (1..4).flat_map do |s|
      %w[own_route_frequency ewa_candidate_w0.5].map do |name|
        {session: s, treatment: 3, variant: name,
         logloss: name == 'own_route_frequency' ? 0.4 : (s == 4 ? 0.0 : 0.6)}
      end
    end
  end

  def test_only_training_sessions_choose_model
    assert_equal 'own_route_frequency', M.choose(fixture, [1, 2, 3], 3)
    assert_equal 'ewa_candidate_w0.5', M.choose(fixture, [4], 3)
  end

  def test_missing_session_is_not_silently_dropped
    missing = fixture.reject { |r| r[:session] == 2 && r[:variant] == 'ewa_candidate_w0.5' }
    assert_raises(RuntimeError) { M.choose(missing, [1, 2, 3], 3) }
  end

  def test_pooled_group_score_can_differ_from_equal_session_score
    # One session supplies 40 groups, the other 80. Equal-session CV treats
    # both sessions equally; R20 historical group-pooled scores do not.
    pooled = (1.0 * 40 + 2.0 * 80) / 120.0
    equal_session = (1.0 + 2.0) / 2.0
    assert_in_delta 5.0 / 3, pooled, 1e-12
    assert_in_delta 1.5, equal_session, 1e-12
    refute_in_delta pooled, equal_session, 1e-12
  end
end
