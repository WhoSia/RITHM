require 'minitest/autorun'
require_relative 'r66_t38_oracle'
class TestR66T38Oracle < Minitest::Test
  O=RithmT38::Oracle;F=O::F
  def test_nested_certificate_and_witness
    s=F.setup;w=F.witness(s,[2,3,4,5],11r/1000)[:floor]
    a,b=O.bounds(s,[2,3,4,5],bins:16);c,d=O.bounds(s,[2,3,4,5],bins:64)
    assert a<=c && c<=d && d<=b;assert_operator b,:>=,w
    l,u=O.bounds(s,[0],bins:64);assert_equal 0,l;assert_operator u,:<,1r/40
    assert_equal [a,b],O.bounds(s,[0,1],bins:16)
    assert_raises(ArgumentError){O.bounds(s,[0],bins:0)}
  end
end
