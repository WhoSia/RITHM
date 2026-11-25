require 'minitest/autorun'
require_relative 'r66_t28_nested'
class TestR66T28Nested < Minitest::Test
  N=RithmT28::Nested;H=RithmT28::Hazard
  def fixture
    rng=Random.new(2802)
    4.times.flat_map do |sid|
      12.times.map do
        b=[1,rng.rand(2),rng.rand(2)];o=b+[rng.rand(3)];p=o+[rng.rand(2)];d=p+[rng.rand(3),rng.rand(2)];r=d+[rng.rand(2)];u=d+[rng.rand(4)]
        [sid,[sid,1,1],[b,o,p,d,r,u,u+[rng.rand(2)]],rng.rand(2)]
      end
    end
  end
  def test_nested_matches_independent_refits
    rows=fixture;grid=[3,12];actual=N.evaluate(rows,grid:grid)
    expected=rows.group_by(&:first).map do |sid,rs|
      train=rows.reject{|r|r.first==sid}
      inner=grid.map{|g|H.evaluate(train,strength:g)[:scores]}
      all,_=H.fit(train);empty=H.tables
      H::MODES.each_with_index.map do |m,i|
        g=grid[grid.each_index.min_by{|j|inner[j][m][:session_logloss]}]
        rs.sum{|r|p=H.predict(r[2],all,empty,strength:g)[i];-Math.log(r.last==1 ? p : 1-p)}/rs.size
      end
    end
    H::MODES.each_with_index{|m,i|assert_in_delta expected.sum{|x|x[i]}/expected.size,actual[:session_logloss][m],1e-12;assert_equal 4,actual[:selected_strength_counts][m].values.sum}
  end
  def test_guards
    assert_raises(ArgumentError){N.evaluate(fixture,grid:[])}
    assert_raises(RuntimeError){N.evaluate(fixture.take(24))}
  end
end
