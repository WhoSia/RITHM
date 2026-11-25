require 'minitest/autorun'
require_relative 'r66_t22_identification'
class TestR66T22Identification < Minitest::Test
  I=RithmT22::Identification
  def delta(k);Array.new(6){|j| j==k ? 1 : 0};end
  def test_exact_deconvolution
    (0..5).each do |k|
      (0..5).each do |j|
        (1..20).each do |i|
          q=Rational(i,20);a=delta(j);p=I.mix(k,a,q)
          assert_equal a,I.recover(k,p,q)
          b=I.bounds(k,p,:a);g=I.gain(a,:a)
          assert_operator g,:>=,b[:low];assert_operator g,:<=,b[:high]
          [b[:q_low],b[:q_high]].select(&:positive?).each{|x| assert_equal p,I.mix(k,I.recover(k,p,x),x)}
        end
      end
    end
  end
  def test_observational_equivalence_with_opposite_active_choice
    p=I.mix(5,delta(3),Rational(1,2))
    assert_equal(-1,I.gain(p,:b))
    assert_equal 2,I.gain(I.recover(5,p,Rational(1,2)),:b)
    assert_equal(-1,I.gain(I.recover(5,p,1),:b))
    assert_equal({low:-1,high:2,q_low:Rational(1,2),q_high:1},I.bounds(5,p,:b))
  end
  def test_identity_and_invalid
    assert_equal 4,I.bounds(5,delta(5),:a)[:low]
    assert_raises(ArgumentError){I.recover(5,delta(3),Rational(1,2))}
    assert_raises(ArgumentError){I.recover(5,delta(5),0)}
    assert_raises(ArgumentError){I.bounds(5,delta(3),:a,q_max:Rational(1,2))}
  end
end
