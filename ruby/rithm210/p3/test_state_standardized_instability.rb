require 'minitest/autorun'
require_relative 'state_standardized_instability'

class TestRithm210StateStandardizedInstability < Minitest::Test
  M=Rithm210StateStandardizedInstability
  def fixture
    (1..24).flat_map do |session|
      (1..3).flat_map do |treatment|
        [:early,:late].flat_map do |epoch|
          [3,4,5].map do |n|
            {session:session,treatment:treatment,epoch:epoch,n:n,
              subsequent:(treatment==3 && epoch==:early ? 6 : 3)}
          end
        end
      end
    end
  end
  def test_uniform_state_weights
    data=M.cell_data(fixture)
    x=M.changes(data,(1..24).to_a)
    assert_in_delta 6,x[:treatments][3][:early],1e-12
    assert_in_delta 3,x[:treatments][3][:late],1e-12
    assert_in_delta 3,x[:full_minus_no_decline],1e-12
  end
  def test_cluster_resampling_respects_multiplicity
    data=M.cell_data(fixture)
    x=M.standardized(data,(1..24).to_a,3,:early)
    y=M.standardized(data,Array.new(48){|i|i%24+1},3,:early)
    assert_in_delta x,y,1e-12
  end
  def test_missing_support_is_error_not_zero
    assert_raises(RuntimeError) do
      M.standardized({},[1],3,:early)
    end
  end
end
