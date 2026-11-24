# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t14_accounting'
class R66T14AccountingTest < Minitest::Test
  A=RithmT14::Accounting;K=RithmT14::Kernel;S=RithmT12::Schedules
  def test_fees_do_not_redefine_private_choices
    [S.common,S.independent,S.fixed_count(3)].each do |s|
      x=A.forecast(n0:5,horizon:40,schedule:s,mechanism: :cognitive,policy: :free_info,switch_fee:2,offer_fee:3)
      y=K.forecast(n0:5,horizon:40,schedule:s,mechanism: :cognitive,policy: :free_info)
      assert_equal y[:congestion],x[:congestion]
      assert_equal 117,x[:offers]
      assert_equal x[:congestion]+2*x[:switches]+3*x[:offers],x[:resource_total]
    end
  end
  def test_free_offer_can_harm_even_before_costs
    [S.common,S.independent,S.fixed_count(3)].each do |s|
      b=A.forecast(n0:5,horizon:40,schedule:s,mechanism: :cognitive)
      f=A.forecast(n0:5,horizon:40,schedule:s,mechanism: :cognitive,policy: :free_info)
      assert_operator f[:congestion],:>,b[:congestion]
      assert_operator f[:switches],:>,b[:switches]
    end
  end
  def test_no_transition_no_fee
    x=A.forecast(n0:5,horizon:1,schedule:S.common,mechanism: :cognitive,policy: :free_info,switch_fee:2,offer_fee:3)
    assert_equal({congestion:3,switches:0,offers:0,resource_total:3},x)
  end
  def test_negative_fee_rejected
    assert_raises(ArgumentError){ A.forecast(n0:5,horizon:4,schedule:S.common,mechanism: :cognitive,switch_fee:-1) }
  end
end
