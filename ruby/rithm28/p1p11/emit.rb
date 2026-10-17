# frozen_string_literal: true
require 'json'
require 'openssl'
module RithmP1P11
  TEST_KEYS={'receipt-test-v1'=>'synthetic-receipt-only-key','delivery-test-v1'=>'synthetic-delivery-only-key'}.freeze
  def self.canonical(e)
    %w[domain issuer person episode event_id occurred published received outcome].map{|k|JSON.generate(e.fetch(k))}.join('|')
  end
  def self.sign(e,key_id)
    e.merge('key_id'=>key_id,'mac'=>OpenSSL::HMAC.hexdigest('sha256',TEST_KEYS.fetch(key_id),canonical(e)))
  end
  def self.sample
    e={'issuer'=>'constructed-institution','person'=>'B2','episode'=>'B2:appeal2','event_id'=>'case-001','occurred'=>0,'published'=>1,'received'=>2}
    a=sign(e.merge('domain'=>'client_receipt','outcome'=>'appeal_acknowledged'),'receipt-test-v1')
    b=sign(e.merge('domain'=>'benefit_delivery','event_id'=>'case-002','occurred'=>3,'published'=>4,'received'=>5,'outcome'=>'benefit_delivered'),'delivery-test-v1')
    {'schema'=>'rithm.p1p11.typed-evidence.v1','synthetic'=>true,'evidence'=>[a,b]}
  end
end
File.write(ARGV.fetch(0),JSON.pretty_generate(RithmP1P11.sample)) if __FILE__==$PROGRAM_NAME
