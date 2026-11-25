# frozen_string_literal: true
require 'csv'
require 'digest'
require 'open3'
require 'json'
module RithmT26
  module SourceContract
    SHA='e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953'
    FILE='data_task_all_switch_230705.csv'
    module_function
    def read_rows(path)
      raise ArgumentError,'source SHA mismatch' unless Digest::SHA256.file(path).hexdigest==SHA
      csv,err,status=Open3.capture3('unzip','-p',path,FILE)
      raise "unzip failure: #{err}" unless status.success?
      CSV.parse(csv,headers:true).reject{|r|%w[2 101].include?(r['session']) || !%w[1 2 3].include?(r['trt'])}
    end
    def audit(path)
      x=summarize(read_rows(path))
      raise 'cohort mismatch' unless x[:rows]==34560 && x[:sessions]==24 && x[:group_transitions]==5616
      x.merge(source_sha256:SHA,aggregate_only:true)
    end
    def summarize(rows,periods:40,actors:6)
      raise ArgumentError,'empty cohort' if rows.empty?
      index={};groups=Hash.new{|h,k|h[k]=[]}
      rows.each do |r|
        period=Integer(r['Period']);route=Integer(r['RouteA']);n=Integer(r['NumA'])
        raise 'schema' unless period.between?(1,periods) && route.between?(0,1) && n.between?(0,actors)
        g=r.values_at('session','Group','trt');key=g+[r['ID'],period]
        raise 'duplicate actor-period' if index.key?(key)
        index[key]=r;groups[g+[period]]<<r
      end
      sums=Hash.new{|h,k|h[k]=Hash.new(0)};sessions=Hash.new{|h,k|h[k]=Hash.new(0)}
      groups.each do |(sid,g,trt,t),rs|
        n=Integer(rs.first['NumA'])
        raise 'group occupancy mismatch' unless rs.size==actors && rs.sum{|r|Integer(r['RouteA'])}==n && rs.all?{|r|Integer(r['NumA'])==n}
        next if t==periods
        ns=0;next_n=0
        rs.each do |r|
          future=index.fetch([sid,g,trt,r['ID'],t+1]);a=Integer(r['RouteA']);b=Integer(future['RouteA']);sw=(a-b).abs
          raise 'lead column mismatch' unless Integer(r['switchWill'])==sw && Integer(r['switchAtoBWill'])==[a-b,0].max && Integer(r['switchBtoAWill'])==[b-a,0].max && Integer(r['NumAnext'])==Integer(future['NumA'])
          ns+=sw;next_n+=b
        end
        raise 'group lead mismatch' unless rs.all?{|r|Integer(r['NumSwitchWill'])==ns && Integer(r['NumAnext'])==next_n}
        [sums['all'],sums[trt],sessions[sid]].each do |x|
          x['group_transitions']+=1;x['actor_transitions']+=actors;x['switches']+=ns
          x['unchanged_occupancy']+=1 if n==next_n
          x['unchanged_with_switches']+=1 if n==next_n && ns>0
        end
      end
      # Session-balanced sensitivity summary; no per-session identifiers or raw rows exported.
      fractions=sessions.values.map{|v|v['unchanged_with_switches'].to_f/v['group_transitions']}
      loo=fractions.each_index.map{|i|(fractions.sum-fractions[i])/(fractions.size-1)} if fractions.size>1
      {rows:rows.size,sessions:sessions.size,group_transitions:sums['all']['group_transitions'],totals:sums.to_h,session_balanced_hidden_turnover:fractions.sum/fractions.size,leave_one_session_out:loo&.minmax}
    end
  end
end
puts JSON.pretty_generate(RithmT26::SourceContract.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
