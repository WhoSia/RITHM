# frozen_string_literal: true
require_relative 'r66_t26_source_contract'
module RithmT27
  module Order
    module_function
    # Conditional on total switches, an exchangeable binary sequence has this expectation.
    def adjacency(s)
      raise ArgumentError,'binary sequence length >= 2' unless s.size>=2 && s.all?{|x|[0,1].include?(x)}
      m=s.sum
      [s.each_cons(2).count{|a,b|a==1 && b==1},Rational(m*(m-1),s.size)]
    end
    # Conditional on starting route and four transition counts, a homogeneous
    # two-state Markov path has uniform positive run-length compositions per route.
    def markov_expected(routes)
      raise ArgumentError,'binary route sequence' unless routes.size>=3 && routes.all?{|x|[0,1].include?(x)}
      runs=routes.chunk_while{|a,b|a==b}.to_a
      [0,1].sum do |a|
        count=runs.count{|r|r.first==a};total=routes.count(a)
        internal=count-(routes.first==a ? 1 : 0)-(routes.last==a ? 1 : 0)
        next 0 if internal<=0
        internal*(total==1 ? 1 : Rational(count-1,total-1))
      end
    end
    def summarize(rows,periods:40)
      raise ArgumentError,'periods' unless periods.is_a?(Integer) && periods>=5
      by_session=Hash.new{|h,k|h[k]=Array.new(3){[0,0,0r,0,0r]}}
      rows.group_by{|r|r.values_at('session','Group','trt','ID')}.each do |id,rs|
        rs=rs.sort_by{|r|Integer(r['Period'])}
        raise 'incomplete trajectory' unless rs.map{|r|Integer(r['Period'])}==(1..periods).to_a
        routes=rs.map{|r|Integer(r['RouteA'])};raise 'route' unless routes.all?{|x|[0,1].include?(x)}
        s=routes.each_cons(2).map{|a,b|(a-b).abs};cut=s.size/2
        [routes,routes.take(cut+1),routes.drop(cut)].each_with_index do |path,i|
          seq=path.each_cons(2).map{|a,b|(a-b).abs}
          observed,expected=adjacency(seq);v=by_session[id[0]][i]
          v[0]+=seq.size-1;v[1]+=observed;v[2]+=expected;v[3]+=1;v[4]+=markov_expected(path)
        end
      end
      raise 'empty cohort' if by_session.empty?
      modes=[:whole,:early,:late]
      modes.each_with_index.to_h do |mode,i|
        vs=by_session.values.map{|v|v[i]};d=vs.map{|pairs,o,e,_,_|(o-e).to_f/pairs};md=vs.map{|pairs,o,_,_,e|(o-e).to_f/pairs}
        n,o,e,m,me=vs.transpose.map(&:sum)
        [mode,{trajectories:m,pairs:n,adjacent_switches:o,exchangeable_expected:e.to_f,session_mean_excess:d.sum/d.size,sessions_positive:d.count(&:positive?),markov_expected:me.to_f,markov_session_mean_excess:md.sum/md.size,markov_sessions_positive:md.count(&:positive?),sessions:vs.size}]
      end
    end
    def audit(path)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      summarize(rows).merge(source_sha256:s::SHA,aggregate_only:true)
    end
  end
end
puts JSON.pretty_generate(RithmT27::Order.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
