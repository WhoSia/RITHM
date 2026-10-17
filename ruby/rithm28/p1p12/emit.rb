# frozen_string_literal: true
require 'json'
require 'openssl'
module RithmP12
 KEYS={'client-log-test-root'=>'synthetic-client-log-secret','provider-test-root'=>'synthetic-provider-secret'}.freeze
 FIELDS=%w[kind issuer person episode id parent occurred published received result].freeze
 def self.sign(record,root)
  m=FIELDS.map{|k|JSON.generate(record.fetch(k))}.join('|')
  record.merge('root'=>root,'mac'=>OpenSSL::HMAC.hexdigest('SHA256',KEYS.fetch(root),m))
 end
 def self.fixture(delivery:true,receipt_published:1,receipt_received:2)
  c={'person'=>'B2','episode'=>'appeal-2'}
  receipt=sign(c.merge('kind'=>'client_receipt','issuer'=>'synthetic-client-log','id'=>'rec-1','parent'=>'','occurred'=>0,'published'=>receipt_published,'received'=>receipt_received,'result'=>'received'),'client-log-test-root')
  records=[receipt]
  if delivery
   records<<sign(c.merge('kind'=>'benefit_delivery','issuer'=>'synthetic-provider','id'=>'pay-1','parent'=>'rec-1','occurred'=>3,'published'=>4,'received'=>5,'result'=>'delivered'),'provider-test-root')
  end
  {'schema'=>'rithm.p1p12.two-roots.v1','synthetic'=>true,'records'=>records}
 end
 def self.observation(doc,at:6)
  doc.fetch('records').select{|e|e['kind']=='client_receipt'&&e['received']<=at}.map{|e|[e.fetch('id'),e.fetch('received'),e.fetch('result')]}.sort
 end
end
File.write(ARGV.fetch(0),JSON.pretty_generate(RithmP12.fixture)) if __FILE__==$PROGRAM_NAME
