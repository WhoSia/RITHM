require 'minitest/autorun'
require_relative 'r66_t21_coordination'
class TestR66T21Coordination < Minitest::Test
  C=RithmT21::Coordination
  def test_clean_boundary
    (0..100).each do |i|
      k=Rational(i,100);q=C.min_receipt(k)
      assert C.noise(q,0,k)[:obedient]
      assert_equal 0,C.noise(q,0,k)[:silent_gain]
      refute C.noise(q/2,0,k)[:obedient] if q>0
      assert C.noise(1,0,k)[:obedient]
    end
    assert_equal Rational(5,13),C.min_receipt(0)
    assert_equal Rational(1,5),C.min_receipt(Rational(1,2))
  end
  def test_exact_bayes_enumeration
    [0,Rational(1,5),Rational(1,2),1].product([0,Rational(1,20),Rational(1,2),1]).each do |q,f|
      mass=[0,0];other=[0,0];cost=0;switch=0
      5.times do |selected|
        32.times do |mask|
          w=Rational(1,5);count=0
          5.times do |i|
            p=i==selected ? q : f;w*=mask[i]==1 ? p : 1-p;count+=mask[i]
          end
          z=mask[0];mass[z]+=w;other[z]+=w*(count-z);cost+=w*3*(1-count)**2;switch+=w*count
        end
      end
      r=C.noise(q,f,0)
      assert_equal 1,mass.sum;assert_equal cost,r[:congestion];assert_equal switch,r[:switches]
      assert_equal 1-3*other[1]/mass[1],r[:received_gain] if mass[1]>0
      assert_equal 1-3*other[0]/mass[0],r[:silent_gain] if mass[0]>0
    end
  end
  def test_false_positive_boundary
    assert C.noise(1,Rational(46,1000),0)[:obedient]
    refute C.noise(1,Rational(47,1000),0)[:obedient]
    assert_equal Rational(-3,40),C.noise(1,Rational(1,20),0)[:received_gain]
  end
  def test_silent_mixed_rival
    (0..20).each do |i|
      (0..20).each do |j|
        q=Rational(i,20);k=Rational(j,20);r=C.silent_mix(q,k)
        assert_operator r[:received_gain],:>=,0
        assert_operator r[:b_gain],:<=,0
        if r[:silent_switch]>0 then assert_equal 0,r[:silent_gain]
        else assert_operator r[:silent_gain],:<=,0 end
      end
    end
  end
  def test_clean_horizon_and_resource_accounting
    assert_equal 3,C.clean_horizon(1,0,horizon:1)[:total]
    assert_equal Rational(9,2),C.clean_horizon(1,0,horizon:2)[:total]
    assert_equal 120,C.clean_horizon(0,1)[:total]
    assert_raises(ArgumentError){C.clean_horizon(Rational(1,10),0)}
    r=C.clean_horizon(Rational(1,2),0,horizon:40,resource:2)
    assert_equal r[:congestion]+2*r[:switches],r[:total]
  end
end
