require 'minitest/autorun'
require_relative 'r66_t20_phase'
class TestR66T20Phase < Minitest::Test
  P=RithmT20::Phase;A=RithmT20::AllMixed
  def test_all_affine_patterns_and_constructive_witness
    [4,5].each do |n|
      assert_equal Rational(4,3),P.intervals(n).map { |x| x[:hi] }.max
      101.times do |i|
        k=Rational(4*i,300); p=P.witness(n,k);s=p.flatten.sum
        p.each_with_index do |ps,j|
          theta=(11+(j==0 ? k : -k))/Rational(3)
          ps.each do |x|
            g=theta-(s-x)
            assert x==0 ? g<=0 : x==1 ? g>=0 : g==0
          end
        end
        r,_=A.row(p);assert_operator r[n],:<,1
      end
      # m=1 can only arise at k=1 or k=2 on this interval; at k=2 all rows stay.
      assert A.actions(n,2).all? { |r,s| r[n]==1 }
      [Rational(4,3)+Rational(1,100),Rational(3,2),Rational(7,4),2].each do |k|
        assert A.actions(n,k).all? { |r,s| r[n]==1 }
      end
    end
  end
end
