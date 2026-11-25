require 'minitest/autorun'
require_relative 'r66_t26_source_contract'
class TestR66T26SourceContract < Minitest::Test
  S=RithmT26::SourceContract
  def rows
    [0,1].flat_map do |session|
      [1,2].flat_map do |t|
        [0,1].map do |i|
          a=t==1 ? i : 1-i;sw=t==1 ? 1 : -1
          {'session'=>session.to_s,'Group'=>'1','trt'=>'3','ID'=>i.to_s,'Period'=>t.to_s,'RouteA'=>a.to_s,'NumA'=>'1','switchWill'=>sw.to_s,'switchAtoBWill'=>(t==1 ? a : -1).to_s,'switchBtoAWill'=>(t==1 ? 1-a : -1).to_s,'NumAnext'=>(t==1 ? 1 : -1).to_s,'NumSwitchWill'=>(t==1 ? 2 : -2).to_s}
        end
      end
    end
  end
  def test_hidden_turnover_and_no_identifiers
    r=S.summarize(rows,periods:2,actors:2)
    assert_equal 2,r[:sessions];assert_equal 2,r[:group_transitions]
    assert_equal({'group_transitions'=>2,'actor_transitions'=>4,'switches'=>4,'unchanged_occupancy'=>2,'unchanged_with_switches'=>2},r[:totals]['all'])
    assert_equal [1.0,1.0],r[:leave_one_session_out]
    refute r.key?(:session_rows)
  end
  def test_reject_leakage_or_schema_mismatch
    x=rows;x[0]['switchWill']='0';assert_raises(RuntimeError){S.summarize(x,periods:2,actors:2)}
    x=rows;x<<x.first.dup;assert_raises(RuntimeError){S.summarize(x,periods:2,actors:2)}
    x=rows;x[0]['NumAnext']='0';assert_raises(RuntimeError){S.summarize(x,periods:2,actors:2)}
    assert_raises(ArgumentError){S.summarize([])}
  end
end
