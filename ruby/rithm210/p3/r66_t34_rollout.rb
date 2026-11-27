# frozen_string_literal: true
require_relative 'r66_t26_source_contract'
module RithmT34
  module Rollout
    S=RithmT26::SourceContract
    COST=(0..6).map{|n|3*(n-4)**2}.freeze
    MODES=[:occupancy,:treatment,:phase].freeze
    HORIZONS=[1,5,10,20].freeze
    module_function
    def paths(rows,periods:40)
      rows.group_by{|r|r.values_at('session','Group','trt')}.map do |(sid,_,trt),rs|
        times=rs.group_by{|r|Integer(r['Period'])};raise 'incomplete group' unless times.keys.sort==(1..periods).to_a
        [sid,trt,(1..periods).map{|t|v=times.fetch(t);raise 'group size' unless v.size==6;v.sum{|r|Integer(r['RouteA'])}}]
      end
    end
    def fit(paths,strength:12)
      raise ArgumentError,'strength' unless strength>0
      c=Array.new(3){Hash.new{|h,k|h[k]=Array.new(7,0)}}
      paths.each do |_,trt,ns|
        (1...ns.size-1).each do |i|
          n=ns[i];j=ns[i+1];[ [n],[n,trt],[n,trt,i/10] ].each_with_index{|k,m|c[m][k][j]+=1}
        end
      end
      c
    end
    def row(c,n,trt,i,mode,strength:12)
      p=Array.new(7,1.0/7)
      [[n],[n,trt],[n,trt,i/10]].take(mode+1).each_with_index do |k,m|
        v=c[m][k];a=m==0 ? 7.0 : strength
        p=v.each_with_index.map{|x,j|(x+a*p[j])/(v.sum+a)}
      end
      p
    end
    def forecast(c,n,trt,i,h,mode,strength:12)
      p=Array.new(7,0.0);p[n]=1;cost=0.0
      h.times do |k|
        q=Array.new(7,0.0)
        p.each_with_index do |w,j|
          next if w==0
          row(c,j,trt,i+k,mode,strength:strength).each_with_index{|a,l|q[l]+=w*a}
        end
        p=q;cost+=p.zip(COST).sum{|a,b|a*b}
      end
      [p,cost]
    end
    def evaluate(paths,strength:12,horizons:HORIZONS)
      sessions=paths.map(&:first).uniq;raise 'need two sessions' unless sessions.size>=2
      folds=sessions.map do |sid|
        c=fit(paths.reject{|r|r.first==sid},strength:strength);f={}
        horizons.each do |h|
          MODES.each_with_index do |m,j|
            n=0;l=0.0;pred=0.0;act=0.0;mse=0.0
            paths.select{|r|r.first==sid}.each do |_,trt,ns|
              (1...ns.size-h).each do |i|
                q,v=forecast(c,ns[i],trt,i,h,j,strength:strength);a=ns[(i+1)..(i+h)].sum{|x|COST[x]}
                n+=1;l-=Math.log(q[ns[i+h]]);pred+=v;act+=a;mse+=(v-a)**2
              end
            end
            raise 'no evaluation origins' if n==0
            f[[h,m]]=[n,l/n,pred/n,act.to_f/n,mse/n]
          end
        end;f
      end
      {sessions:sessions.size,strength:strength,results:horizons.map{|h|{horizon:h,models:MODES.map{|m|v=folds.map{|f|f[[h,m]]};{mode:m,origins:v.sum(&:first),endpoint_logloss:v.sum{|x|x[1]}/v.size,predicted_cumulative_cost:v.sum{|x|x[2]}/v.size,actual_cumulative_cost:v.sum{|x|x[3]}/v.size,cumulative_cost_mse:v.sum{|x|x[4]}/v.size}}}}}
    end
    def recovery(paths)
      # Descriptive observed state transitions, no intervention or constant reset probability.
      (0..6).map do |n|
        count=Array.new(7,0)
        paths.each{|_,_,ns|ns.each_cons(2){|a,b|count[b]+=1 if a==n}}
        {state:n,transitions:count.sum,counts:count,return_to_four:count[4].fdiv(count.sum),return_to_five:count[5].fdiv(count.sum)}
      end
    end
    def audit(path)
      rows=S.read_rows(path);c=S.summarize(rows);raise 'cohort mismatch' unless c[:rows]==34560 && c[:sessions]==24 && c[:group_transitions]==5616
      ps=paths(rows);evaluate(ps).merge(recovery:recovery(ps),source_sha256:S::SHA,aggregate_only:true)
    end
  end
end
puts JSON.pretty_generate(RithmT34::Rollout.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
