require 'minitest/autorun'
require 'tempfile'
require 'digest'
require_relative 'r19_ssm_source_benchmark'
class TestRithm210R19SSMSourceBenchmark < Minitest::Test
  M=Rithm210R19SSMSourceBenchmark
  def fixture
    Tempfile.create(['ssm_fixture','.csv']) do |f|
      f.write("session,section,trt,Period,ID,profit,Informed,RouteA,NumA\n")
      f.write("102,1,1,1,7,10.0,0,1,NOT_PUBLIC\n")
      f.write("102,1,1,2,7,8.2,0,0,NOT_PUBLIC\n")
      f.flush
      old=M::ORIGINAL_SHA
      begin
        M.send(:remove_const,:ORIGINAL_SHA)
        M.const_set(:ORIGINAL_SHA,Digest::SHA256.file(f.path).hexdigest)
        yield f.path
      ensure
        M.send(:remove_const,:ORIGINAL_SHA)
        M.const_set(:ORIGINAL_SHA,old)
      end
    end
  end
  def test_prior_only_and_uninformed_no_private_occupancy
    fixture do |path|
      x=M.run(path,q_values:[1])
      assert_equal 1,x[:sessions]
      assert_equal 2,x[:individual_periods]
      s=x[:by_treatment_information_model].find{|v|v[:model]=='ssm_1'}
      assert_in_delta 0.25,s[:brier],1e-12
      b=x[:by_treatment_information_model].find{|v|v[:model]=='own_route_frequency'}
      assert_operator b[:brier],:>,s[:brier]
      assert_equal 2,x[:session_scores].size
    end
  end
  def test_bad_hash_and_q_rejected
    Tempfile.create(['bad_source','.csv']) do |f|
      f.write('not source');f.flush
      assert_raises(RuntimeError){M.run(f.path)}
    end
    fixture{|path|assert_raises(ArgumentError){M.run(path,q_values:[10])}}
  end
end
