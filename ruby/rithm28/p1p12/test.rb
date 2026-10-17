require 'minitest/autorun'
require_relative 'emit'
require 'json'
require 'tempfile'
class TestTwoRootEvidence < Minitest::Test
 def verify(doc)
  Tempfile.create(['rithm-p1p12','.json']){|f|f.write(JSON.generate(doc));f.flush;out=IO.popen(['go','run',File.join(__dir__,'../../../go/rithm28/p1p12/verify.go'),f.path],err:[:child,:out], &:read);[out,$?.exitstatus]}
 end
 def re_sign(d)
  RithmP12.sign(d.reject{|k|%w[root mac].include?(k)},'provider-test-root')
 end
 def test_chain
  output,status=verify(RithmP12.fixture)
  assert_equal 0,status;assert_includes output,'synthetic_delivery_chain_only';assert_includes output,'real_world_welfare_verified=false'
 end
 def test_receipt_only
  output,status=verify(RithmP12.fixture(delivery:false))
  assert_equal 0,status;assert_includes output,'receipt_only_unconfirmed'
 end
 def test_wrong_parent_re_signed
  x=RithmP12.fixture;x['records'][1]['parent']='wrong';x['records'][1]=re_sign(x['records'][1]);refute_equal 0,verify(x)[1]
 end
 def test_wrong_person_re_signed
  x=RithmP12.fixture;x['records'][1]['person']='A1';x['records'][1]=re_sign(x['records'][1]);refute_equal 0,verify(x)[1]
 end
 def test_tampered_mac
  x=RithmP12.fixture;x['records'][0]['mac']='00';refute_equal 0,verify(x)[1]
 end
 def test_publication_metadata_noninterference
  a=RithmP12.fixture(receipt_published:1);b=RithmP12.fixture(receipt_published:2)
  assert_equal RithmP12.observation(a),RithmP12.observation(b)
  refute_equal a['records'][0]['mac'],b['records'][0]['mac']
  assert_equal 0,verify(a)[1];assert_equal 0,verify(b)[1]
 end
end