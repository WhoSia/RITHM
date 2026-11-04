require 'minitest/autorun'
require_relative 'churn_session_bootstrap'
class TestRithm210ChurnSessionBootstrap < Minitest::Test
  M=Rithm210ChurnSessionBootstrap
  def test_gross_turnover_vs_cancelling_churn
    rows=(1..24).flat_map do |session|
      [1,3].flat_map do |treatment|
        [:early,:late].map do |epoch|
          up=treatment==3 && epoch==:early ? 1 : 0
          {session:session,treatment:treatment,epoch:epoch,
            u:up,d:0,change:up}
        end
      end
    end
    totals=M.summaries(rows)
    a=M.contrast(totals,(1..24).to_a,1)
    assert_in_delta 1,a[:full_decline],1e-12
    assert_in_delta 0,a[:no_decline],1e-12
    assert_in_delta 1,a[:full_minus_no],1e-12
    b=M.contrast(totals,(1..24).to_a,2)
    assert_in_delta 0,b[:full_decline],1e-12
  end
end
