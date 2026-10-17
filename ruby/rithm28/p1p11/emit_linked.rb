# frozen_string_literal: true
require 'json'
require 'openssl'
module RithmP1P11V2
  TEST_KEYS={'receipt-test-v2'=>'synthetic-receipt-role-secret','delivery-test-v2'=>'synthetic-delivery-role-secret'}.freeze
  SIGNED=%w[domain issuer person episode event_id parent_event_id occurred published received outcome].freeze
  def self.mac(e,key)
    msg=SIGNED.map{|k|JSON.generate(e.fetch(k))}.join('|')
    OpenSSL::HMAC.hexdigest('sha256',TEST_KEYS.fetch(key),msg)
  end
  def self.sign(event,key)
    event.merge('key_id'=>key,'mac'=>mac(event,key))
  end
  def self.sample
    base={'issuer'=>'synthetic-agency','person'=>'B2','episode'=>'B2:appeal2'}
    receipt=sign(base.merge('domain'=>'client_receipt','event_id'=>'receipt-001','parent_event_id'=>'','occurred'=>0,'published'=>1,'received'=>2,'outcome'=>'appeal_acknowledged'),'receipt-test-v2')
    delivery=sign(base.merge('domain'=>'benefit_delivery','event_id'=>'delivery-001','parent_event_id'=>'receipt-001','occurred'=>3,'published'=>4,'received'=>5,'outcome'=>'benefit_delivered'),'delivery-test-v2')
    {'schema'=>'rithm.p1p11.linked-evidence.v2','synthetic'=>true,'evidence'=>[receipt,delivery]}
  end
end
if __FILE__==$PROGRAM_NAME
  File.write(ARGV.fetch(0),JSON.pretty_generate(RithmP1P11V2.sample))
end