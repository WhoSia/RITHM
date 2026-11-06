require 'minitest/autorun'
require_relative 'r21_ewa_group_cv'

class TestRithm210R21EWAGroupCV < Minitest::Test
  M = Rithm210R21EWAGroupCV
  def params
    M::Params.new(phi: 0.5, rho: 0.5, delta: 0.8, beta: 0.5)
  end
  def test_initial_and_informed_counterfactual
    no = M::Learner.new(params)
    yes = M::Learner.new(params)
    assert_in_delta 0.5, no.prob_a, 1e-12
    no.update(route_a: true, n_a: 4, informed: false)
    yes.update(route_a: true, n_a: 4, informed: true)
    assert_operator no.prob_a, :<, 0.5
    assert_operator yes.prob_a, :>, 0.5
  end
  def test_uninformed_signal_not_revealed
    a = M::Learner.new(params)
    b = M::Learner.new(params)
    a.update(route_a: true, n_a: 4, informed: false)
    b.update(route_a: true, n_a: 4, informed: false)
    assert_in_delta a.prob_a, b.prob_a, 1e-12
  end
  def test_route_own_bit_correction
    x = M::Learner.new(params)
    x.update(route_a: false, n_a: 4, informed: true)
    assert_in_delta 0.5, x.prob_a, 1e-12
  end
  def test_grid_and_stable_logistic
    assert_equal 24, M.grid.size
    extreme = M::Params.new(phi: 0.9, rho: 1.0, delta: 0.0, beta: 10_000.0)
    learner = M::Learner.new(extreme)
    learner.update(route_a: true, n_a: 6, informed: false)
    assert learner.prob_a.finite?
    assert learner.prob_a.between?(0.0, 1.0)
  end
  def test_invalid_updates
    x = M::Learner.new(params)
    assert_raises(ArgumentError) { x.update(route_a: 0, n_a: 4, informed: false) }
    assert_raises(ArgumentError) { x.update(route_a: true, n_a: 0, informed: false) }
    assert_raises(ArgumentError) { x.update(route_a: true, n_a: 7, informed: false) }
  end
end

class TestRithm210R21BlendSourceFree < Minitest::Test
  M = Rithm210R21EWAGroupCV
  B = Rithm210R20GroupBridge

  def test_zero_ewa_blend_is_exact_prior_only_frequency
    params = M.grid.first
    groups = {}
    (1..2).each do |t|
      groups[[42, 1, t, 1]] = (1..6).map do |id|
        route = (id <= 3 ? 1 : 0)
        {'ID' => id.to_s, 'RouteA' => route.to_s,
         'NumA' => '3', 'trt' => '3', 'Informed' => '1'}
      end
    end
    scored = M.predict_scores(groups, params, blend: 0.0)
    assert_equal 2, scored.size
    fair = B.score(Array.new(6, 0.5), 3)
    second = B.score(Array.new(3, 2.0 / 3) + Array.new(3, 1.0 / 3), 3)
    assert_in_delta fair[:logloss], scored[0][:logloss], 1e-12
    assert_in_delta second[:logloss], scored[1][:logloss], 1e-12
    assert_raises(ArgumentError) { M.predict_scores(groups, params, blend: -0.1) }
  end
end
