require 'minitest/autorun'
require_relative 'latent_shock_residual_counterexample'
class TestRithm210LatentShockResidualCounterexample < Minitest::Test
  M=Rithm210LatentShockResidualCounterexample
  def test_mixture_covariance_closed_form
    rows=M.actor_scenarios(mask:15,strength:0.7,tremble:0.05,shock_amplitude:2.0)
    a,b=rows[0],rows[1]
    joint=(a[:p_plus]*b[:p_plus]+a[:p_minus]*b[:p_minus])/2.0
    assert_in_delta joint-a[:marginal]*b[:marginal],M.covariance(a,b),1e-12
    assert_operator M.covariance(a,b),:>,0
  end
  def test_negative_signed_pair_welfare_without_peer_influence
    x=M.summary
    assert_operator x[:mean_same_route_cov],:>,0
    assert_operator x[:mean_opposing_route_cov],:>,0
    assert_operator x[:signed_pair_excess_welfare],:<,0
    assert_in_delta(-0.932150507,x[:signed_pair_excess_welfare],1e-8)
    assert_in_delta x[:signed_pair_excess_welfare],
      x[:shock_mixture_excess]-x[:independent_marginal_excess],1e-9
  end
end
