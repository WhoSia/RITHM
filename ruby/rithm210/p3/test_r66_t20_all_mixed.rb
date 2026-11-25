require 'minitest/autorun'
require_relative 'r66_t20_all_mixed'
class TestR66T20AllMixed < Minitest::Test
  A=RithmT20::AllMixed; D=RithmT20::Dynamic
  def test_contains_restricted_and_checks_all_profile_best_responses
    (0..6).each do |n|
      [0,Rational(4,9),Rational(1,2),Rational(4,7),Rational(3,4),1,Rational(5,4),2].each do |k|
        acts=A.actions(n,k)
        D.actions(n,k).each { |x| assert_includes acts,x }
        A.profile_pairs(n,k).each do |pairs|
          s=pairs.flatten.sum
          pairs.each_with_index do |ps,i|
            theta=(11+(i==0 ? k : -k))/Rational(3)
            ps.each do |p|
              g=theta-(s-p)
              assert p==0 ? g<=0 : p==1 ? g>=0 : g==0
            end
          end
          row,moves=A.row(pairs)
          assert_equal 1,row.sum;assert_operator moves,:>=,0
        end
      end
    end
  end
  def test_bounds_include_restricted
    [0,Rational(1,2),Rational(3,4),1,2].each do |k|
      r=A.bounds(horizon:8,kappa:k,resource:k);d=D.bounds(horizon:8,kappa:k,resource:k)
      (0..6).each do |n|
        assert_operator r[:lo][n],:<=,d[:lo][n]
        assert_operator r[:hi][n],:>=,d[:hi][n]
      end
    end
  end
end
