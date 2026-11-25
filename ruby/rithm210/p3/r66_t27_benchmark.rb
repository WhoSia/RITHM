require 'benchmark';require_relative 'r66_t27_stability'
S=RithmT27::Stability;C=RithmT27::Compare;rng=Random.new(2701)
rows=8.times.flat_map do |sid|
  400.times.map do
    b=[rng.rand(3),rng.rand(2),rng.rand(2)];o=rng.rand(6);h=rng.rand(2);d=rng.rand(5);f=rng.rand(4);g=rng.rand(4)
    ks=[b,b+[o],b+[h],b+[o,h],b+[o,d],b+[o,f],b+[o,g],b+[o,h,d,f],b+[o,h,d,f,g]]
    [sid,ks,rng.rand(2)]
  end
end
slow=-> {rows.group_by(&:first).keys.map{|sid|C.evaluate(rows.reject{|r|r.first==sid})[:contrasts]}}
3.times do |i|
  a,b= i.even? ? [Benchmark.realtime{slow.call},Benchmark.realtime{S.deletion(rows)}] : (y=Benchmark.realtime{S.deletion(rows)};[Benchmark.realtime{slow.call},y])
  puts "direct=#{a} grouped=#{b} ratio=#{a/b}"
end
