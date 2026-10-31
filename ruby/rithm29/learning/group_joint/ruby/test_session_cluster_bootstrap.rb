require 'minitest/autorun'
require_relative 'session_cluster_bootstrap'
class SessionClusterBootstrapTest < Minitest::Test
  def test_zero_diff_is_exact
    r=RithmSessionBootstrap.interval(Array.new(24,0.0),draws:1000)
    assert_equal 0.0,r[:mean]
    assert_equal 0.0,r[:lower]
    assert_equal 0.0,r[:upper]
  end
  def test_seed_repeatability
    a=RithmSessionBootstrap.interval([-0.4,0.1,-0.2,0.0],draws:1000)
    b=RithmSessionBootstrap.interval([-0.4,0.1,-0.2,0.0],draws:1000)
    assert_equal a,b
    assert_operator a[:lower],:<=,a[:mean]
    assert_operator a[:upper],:>=,a[:mean]
  end
  def test_paired_loss_direction
    d=RithmSessionBootstrap.paired_differences([{'old'=>.9,'new'=>.7}],baseline:'old',candidate:'new')
    assert_in_delta(-.2,d.fetch(0),1e-12)
  end
end
