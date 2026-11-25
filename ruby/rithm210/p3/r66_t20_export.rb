require_relative 'r66_t20_all_mixed'
require 'csv'
CSV($stdout) do |csv|
  csv << %w[kappa resource initial restricted_lo restricted_hi all_lo all_hi]
  [0,Rational(1,4),Rational(4,9),Rational(1,2),Rational(4,7),Rational(3,5),Rational(3,4),Rational(99,100),1,Rational(5,4),Rational(4,3),2].each do |k|
    [0,k].uniq.each do |c|
      a=RithmT20::AllMixed.bounds(horizon:40,kappa:k,resource:c)
      d=RithmT20::Dynamic.bounds(horizon:40,kappa:k,resource:c)
      (0..6).each { |n| csv << [k,c,n,d[:lo][n],d[:hi][n],a[:lo][n],a[:hi][n]] }
    end
  end
end
