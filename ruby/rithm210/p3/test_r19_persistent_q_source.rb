require 'minitest/autorun'
require 'tempfile'
require 'digest'
require_relative 'r19_persistent_q_source'
class TestRithm210R19PersistentQSource < Minitest::Test
  M=Rithm210R19PersistentQSource
  def fixture
    Tempfile.create(['q_filter','.csv']) do |f|
      f.write("session,section,trt,Period,ID,profit,Informed,RouteA,NumA\n")
      f.write("102,1,1,1,7,10.0,0,1,WITHHELD\n")
      f.write("102,1,1,2,7,8.2,0,0,WITHHELD\n")
      f.flush
      old=M::SOURCE_SHA
      begin
        M.send(:remove_const,:SOURCE_SHA)
        M.const_set(:SOURCE_SHA,Digest::SHA256.file(f.path).hexdigest)
        yield f.path
      ensure
        M.send(:remove_const,:SOURCE_SHA)
        M.const_set(:SOURCE_SHA,old)
      end
    end
  end
  def test_filtration_and_posterior_prior_contract
    fixture do |path|
      x=M.run(path,qmax:3)
      assert_equal 1,x[:sessions]
      assert_equal 2,x[:individual_periods]
      assert_equal 3,x[:results].size
      a=x[:results].to_h{|r|[r[:model],r[:brier]]}
      assert_in_delta 0.25,a[:persistent],1e-12
      assert_in_delta 0.25,a[:uniform_prior],1e-12
      assert_operator a[:own_route_frequency],:>,0.25
    end
  end
  def test_sha_and_invalid_q
    Tempfile.create('not_original'){|f|f.write('not_original');f.flush;assert_raises(RuntimeError){M.run(f.path)}}
    fixture{|path|assert_raises(ArgumentError){M.run(path,qmax:10)}}
  end
end
