require 'minitest/autorun'
require_relative 'r18_sign_reduction'
class TestRithm210R18SignReduction < Minitest::Test
  S=Rithm210R18SignReduction
  R=Rithm210R18RandomizationInference
  def test_combinatorial_resolution
    assert_equal 6,S.choose(4,2)
    assert_equal 70,S.choose(8,4)
    assert_equal 2_704_156,S.choose(24,12)
    assert_in_delta 1.0/3,S.minimum_two_sided_p(4),1e-12
    assert_in_delta 1.0/35,S.minimum_two_sided_p(8),1e-12
  end
  def test_sign_reduced_equals_full_exact_four_and_eight
    [4,8].each do |n|
      ids=(1..n).to_a
      assign=R.randomize_sessions(ids,seed:54)
      outcome=ids.to_h{|id|[id,id**2+id/3.0]}
      full=R.fisher_sharp_null(assign,outcome)
      reduced=S.exact_sharp_null(assign,outcome)
      assert_in_delta full[:p_two_sided],reduced[:p_two_sided],1e-12
      assert_in_delta full[:observed],reduced[:observed],1e-12
      assert_equal S.choose(n,n/2),reduced[:assignments]
    end
  end
  def test_four_clusters_cannot_reject_at_five_percent
    ids=(1..4).to_a
    assign=R.randomize_sessions(ids,seed:2)
    outcome={1=>0.0,2=>1.0,3=>4.0,4=>10.0}
    assert_operator S.exact_sharp_null(assign,outcome)[:p_two_sided],:>=,1.0/3
  end
  def test_invalid_inputs
    assert_raises(ArgumentError){S.choose(5,6)}
    assert_raises(ArgumentError){S.minimum_two_sided_p(6)}
    ids=(1..20).to_a
    a=R.randomize_sessions(ids)
    y=ids.to_h{|i|[i,i.to_f]}
    assert_raises(ArgumentError){S.exact_sharp_null(a,y)}
  end
end
