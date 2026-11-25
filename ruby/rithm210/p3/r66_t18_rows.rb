# frozen_string_literal: true
require_relative 'r66_t18_learning'
module RithmT18
  # Full-disclosure-only unrestricted row learner; no private-state leakage.
  class Rows
    def initialize(rho:0.45,strength:4.0,forget:0.0)
      raise ArgumentError,'parameters' unless rho>=0 && rho<1 && strength>0 && forget.between?(0,1)
      @prior=(0..5).map { |k| BASE.each_with_index.map { |b,j| strength*(rho*(k==j ? 1 : 0)+(1-rho)*b) } }
      @evidence=Array.new(6){Array.new(6,0.0)}; @last=nil; @forget=forget; @pred=BASE.dup
    end
    attr_reader :pred
    def observe(k)
      raise ArgumentError,'state' unless (0..5).include?(k)
      @evidence.each { |row| row.map! { |v| (1-@forget)*v } } if @forget>0
      @evidence[@last][k]+=1 if @last
      @last=k
      w=@prior[k].zip(@evidence[k]).map { |p,e| p+e }; z=w.sum
      @pred=w.map { |v| v/z }
    end
  end
  module Full
    module_function
    def run(tape:,clock:,response:,mode:,n:5,strength:4.0)
      raise ArgumentError,'mode' unless [:fixed,:sticky,:rows,:rows_forget].include?(mode)
      actors=Array.new(6) { |i| mode==:fixed ? Filter.new([0.45]) : mode==:sticky ? Filter.new([0.25,0.65]) : Rows.new(strength:strength,forget:mode==:rows_forget ? 0.25 : 0.0) }
      routes=Array.new(6){ |i| i<n };cost=3*(n-4)**2;paths=[]
      tape.each do |values,du,au,eu,shared|
        active=RithmT18.eligible(clock,au,shared);new_routes=routes.dup
        ks=routes.map { |a| n-(a ? 1 : 0) }; paths<<ks
        actors.each_with_index do |f,i|
          a=routes[i];k=ks[i];y=6.5+values[i]-(a ? k+1 : 2*(6-k))
          if f.is_a?(Rows)
            gain=f.observe(k).each_with_index.sum { |p,j| p*(3*j-11) }*(a ? 1 : -1)
          else
            gain=f.observe(a ? :a : :b,y,disclosed_k:k)
          end
          new_routes[i]=!a if active[i] && gain>1e-12 && eu[i]<response
        end
        routes=new_routes;n=routes.count(true);cost+=3*(n-4)**2
      end
      {cost:cost,paths:paths}
    end
    # Same realized paths for all rival predictors: prequential full-state score.
    def replay(paths,strength:4.0)
      models={fixed:Array.new(6){Filter.new([0.45])},sticky:Array.new(6){Filter.new([0.25,0.65])},rows:Array.new(6){Rows.new(strength:strength)},rows_forget:Array.new(6){Rows.new(strength:strength,forget:0.25)}}
      models.transform_values do |actors|
        loss=0.0
        paths.each_with_index do |ks,t|
          actors.each_with_index do |f,i|
            k=ks[i]; p=f.is_a?(Rows) ? f.pred : f.marginal
            loss-=Math.log(p[k]) if t>0
            f.is_a?(Rows) ? f.observe(k) : f.observe(:a,9,disclosed_k:k)
          end
        end
        loss/(6*(paths.size-1))
      end
    end
  end
end
