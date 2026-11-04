require 'minitest/autorun'
require 'tempfile'
require 'csv'
require_relative 'original_welfare_audit'

class TestRithm210OriginalWelfareAudit < Minitest::Test
  M=Rithm210OriginalWelfareAudit
  HEADERS=%w[session section trt Period Group ID NumA NumAnext RouteA Cost Value profit switchBtoAWill switchAtoBWill].freeze

  def with_group(cost_override:nil)
    Tempfile.create(['rithm_welfare','.csv']) do |f|
      csv=CSV.new(f)
      csv << HEADERS
      6.times do |i|
        route_a=i<4 ? 1 : 0
        cost=cost_override && i==0 ? cost_override : 4
        fields=[3,2,1,1,1,i+1,4,4,route_a,cost,10,10-cost,0,0]
        csv << fields
      end
      csv.flush
      f.flush
      yield f.path
    end
  end

  def test_synthetic_source_contract
    with_group do |path|
      result=M.read_groups(path,expected_groups:1)
      assert_equal 1,result.size
      assert_equal 24,result.first[:cost]
      assert_equal 0,result.first[:excess]
      assert_equal 6,result.first[:persons]
      assert_equal 'early',result.first[:epoch]
    end
  end
  def test_catches_mismatched_individual_cost
    with_group(cost_override:7) do |path|
      assert_raises(RuntimeError){M.read_groups(path,expected_groups:1)}
    end
  end
  def test_treatment_period_paired_bootstrap
    rows=(1..24).flat_map do |session|
      (1..3).flat_map do |treatment|
        %w[early late].map do |epoch|
          {session:session,treatment:treatment,epoch:epoch,
           excess:(treatment==3 && epoch=='early' ? 3 : 0)}
        end
      end
    end
    result=M.paired_session_bootstrap(rows,draws:120)
    assert_in_delta 3.0,result[:point],1e-12
    assert_in_delta 3.0,result[:lower],1e-12
    assert_in_delta 3.0,result[:upper],1e-12
    assert_equal 24,result[:session_count]
  end
  def test_epoch_windows
    assert_equal 'early',M.epoch(10)
    assert_equal 'middle',M.epoch(11)
    assert_equal 'middle',M.epoch(29)
    assert_equal 'late',M.epoch(30)
  end
end
