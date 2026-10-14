require 'minitest/autorun'
require_relative 'synthesis'
class P0R5Test < Minitest::Test
 EXPECT={0=>{safe:512,zero:nil,one:7.0/12},1=>{safe:2420,zero:5.0/6,one:5.0/12},2=>{safe:2420,zero:7.0/6,one:0.5}}
 def test_full_synthesis
  EXPECT.each{|lag,w|
   r=rithm28_p0r5_synth(lag,false)
   assert_equal 4104,r[:count];assert_equal w[:safe],r[:safe_count]
   w[:zero] ? assert_in_delta(w[:zero],r[:best][0][:value],1e-10) : assert_nil(r[:best][0])
   assert_in_delta w[:one],r[:best][1][:value],1e-10
  }
 end
 def test_spill_accounting
  EXPECT.each{|lag,w|
   r=rithm28_p0r5_synth(lag,true)
   assert_equal w[:safe],r[:safe_count];assert_in_delta w[:one],r[:best][1][:value],1e-10
  }
 end
 def test_independent_witness_inputs
  [[0,1,1,1,7.0/12],[1,0,1,0,5.0/6],[1,1,33,3,5.0/12],[2,0,1,0,7.0/6],[2,1,1,1,0.5]].each{|lag,b,a,u,w|
   v,s,overflow,n,_=R5.new(lag:lag,bits:b,act:a,update:u).evaluate
   assert_in_delta w,v,1e-10;assert s;refute overflow;assert_operator n,:>,0
  }
 end
 def test_overflow_and_unsafety
  v,s,overflow,n,spill=R5.new(lag:1,bits:0,act:0,update:0,spill:true).evaluate
  refute s;assert overflow;assert spill
 end
end
