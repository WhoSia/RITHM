# frozen_string_literal: true
require 'benchmark'
require_relative 'r66_t28_nested'
H=RithmT28::Hazard;N=RithmT28::Nested;rng=Random.new(2803)
rows=6.times.flat_map do |sid|
  120.times.map do
    b=[1,rng.rand(2),rng.rand(2)];o=b+[rng.rand(3)];p=o+[rng.rand(4)];d=p+[rng.rand(5),rng.rand(4)];r=d+[rng.rand(2)];u=d+[rng.rand(5)]
    [sid,[sid,1,1],[b,o,p,d,r,u,u+[rng.rand(2)]],rng.rand(2)]
  end
end
grid=[3,12,48,192]
direct=lambda do
  scores=rows.group_by(&:first).map do |sid,rs|
    train=rows.reject{|r|r.first==sid};inner=grid.map{|g|H.evaluate(train,strength:g)[:scores]}
    all,_=H.fit(train);empty=H.tables
    H::MODES.each_with_index.map do |m,i|
      g=grid[grid.each_index.min_by{|j|inner[j][m][:session_logloss]}]
      rs.sum{|r|p=H.predict(r[2],all,empty,strength:g)[i];-Math.log(r.last==1 ? p : 1-p)}/rs.size
    end
  end
  H::MODES.each_with_index.to_h{|m,i|[m,scores.sum{|x|x[i]}/scores.size]}
end
3.times do |i|
  a=b=nil;x=y=nil
  if i.even?
    x=Benchmark.realtime{a=direct.call};y=Benchmark.realtime{b=N.evaluate(rows,grid:grid)[:session_logloss]}
  else
    y=Benchmark.realtime{b=N.evaluate(rows,grid:grid)[:session_logloss]};x=Benchmark.realtime{a=direct.call}
  end
  error=a.keys.map{|k|(a[k]-b[k]).abs}.max;raise 'mismatch' unless error<1e-12
  puts "direct=#{x} grouped=#{y} ratio=#{x/y} max_error=#{error}"
end
