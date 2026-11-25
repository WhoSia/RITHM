# frozen_string_literal: true
require_relative 'r66_t28_hazard'
module RithmT28
  module Nested
    H=Hazard
    GRID=[3,12,48,192].freeze
    module_function
    def counts(keys,all,excluded)
      keys.each_with_index.map do |key,i|
        n,y=all[i][key]
        excluded.each{|table|a,b=table[i][key];n-=a;y-=b}
        raise 'invalid training count' unless n>=0 && y.between?(0,n)
        [n,y]
      end
    end
    def losses(grouped,all,excluded,grid)
      totals=grid.map{Array.new(H::MODES.size,0.0)};n=0
      grouped.each do |ks,(count,y)|
        c=counts(ks,all,excluded);n+=count
        grid.each_with_index do |strength,g|
          H.probabilities(c,strength).each_with_index{|p,i|totals[g][i]-=y*Math.log(p)+(count-y)*Math.log(1-p)}
        end
      end
      totals.map{|row|row.map{|v|v/n}}
    end
    # Model-specific hyperparameter choice using only inner held-out sessions.
    def evaluate(records,grid:GRID)
      raise ArgumentError,'grid' unless !grid.empty? && grid.all?{|x|x>0} && grid.uniq==grid
      all,held=H.fit(records);raise 'need at least three sessions' unless held.size>=3
      grouped=records.group_by(&:first).transform_values{|rs|rs.group_by{|r|r[2]}.transform_values{|v|[v.size,v.sum(&:last)]}}
      chosen=H::MODES.to_h{|m|[m,Hash.new(0)]};folds=[]
      grouped.each_key do |outer|
        inner=grouped.filter_map do |val,rows|
          next if val==outer
          losses(rows,all,[held.fetch(outer),held.fetch(val)],grid)
        end
        best=H::MODES.each_index.map do |i|
          grid.each_index.min_by{|g|inner.sum{|v|v[g][i]}}
        end
        outer_scores=losses(grouped.fetch(outer),all,[held.fetch(outer)],grid)
        folds<<best.each_with_index.map do |g,i|
          chosen[H::MODES[i]][grid[g]]+=1;outer_scores[g][i]
        end
      end
      mean=H::MODES.each_with_index.to_h{|m,i|[m,folds.sum{|v|v[i]}/folds.size]}
      contrasts=[[3,4],[3,5],[4,5],[5,6]].to_h do |i,j|
        d=folds.map{|v|v[j]-v[i]};["#{H::MODES[j]}_minus_#{H::MODES[i]}",{mean:d.sum/d.size,better:d.count(&:negative?)}]
      end
      {sessions:held.size,records:records.size,grid:grid,session_logloss:mean,selected_strength_counts:chosen,contrasts:contrasts}
    end
    def audit(path)
      s=RithmT26::SourceContract;rows=s.read_rows(path);check=s.summarize(rows)
      raise 'cohort mismatch' unless check[:rows]==34560 && check[:sessions]==24 && check[:group_transitions]==5616
      records=H.records(rows)
      {fixed:GRID.map{|v|H.evaluate(records,strength:v)},nested:evaluate(records),source_sha256:s::SHA,aggregate_only:true}
    end
  end
end
puts JSON.pretty_generate(RithmT28::Nested.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
