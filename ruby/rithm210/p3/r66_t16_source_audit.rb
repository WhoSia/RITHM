# frozen_string_literal: true
require 'digest'
require 'csv'
require 'open3'
require 'json'
require_relative 'r66_t16_belief'
module RithmT16
  module SourceAudit
    module_function
    SHA='e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953'
    def classify(route,payoff)
      p=Belief.posterior([1]*6,route,payoff)
      support=(0..5).select { |k| p[k]>0 }
      {support:support,sign_known:support.map { |k| Belief.gain(k,route)>0 }.uniq.length==1}
    end
    def audit(path)
      raise ArgumentError,'source SHA mismatch' unless Digest::SHA256.file(path).hexdigest==SHA
      csv,err,status=Open3.capture3('unzip','-p',path,'data_task_all_switch_230705.csv')
      raise "unzip failure: #{err}" unless status.success?
      counts=Hash.new { |h,k| h[k]=Hash.new(0) }; sessions={}; groups=Hash.new { |h,k| h[k]=0 }; endogenous_rows=0; endogenous_adjusted=0
      CSV.parse(csv,headers:true).each do |row|
        sid=Integer(row['session']); next if [2,101].include?(sid)
        trt=Integer(row['trt']); info=Integer(row['Informed']); a=Integer(row['RouteA']); route=a==1 ? :a : :b
        raise 'source schema' unless (1..4).include?(trt) && [0,1].include?(info) && [0,1].include?(a)
        n=Integer(row['NumA']); k=n-a; y=Rational(row['profit']); v=Rational(row['Value']); c=Rational(row['Cost'])
        raise 'cost or value discrepancy' unless c==Belief.cost(k,route) && (6..16).cover?(v)
        if trt==4
          endogenous_rows+=1; endogenous_adjusted+=1 if y!=v-c; next
        end
        raise 'Part 1 payoff discrepancy' unless y==v-c
        x=classify(route,y); raise 'true state not supported' unless x[:support].include?(k)
        key="#{trt}:#{info}:#{route}"; z=counts[key]; z['rows']+=1; z['unique']+=1 if x[:support].length==1
        z['sign_known']+=1 if x[:sign_known];z['support_sum']+=x[:support].length
        z["support_#{x[:support].length}"]+=1
        sessions[sid]=true;groups[[sid,row['Group'],trt,row['Period']]]+=1
      end
      raise 'source count' unless counts.values.sum { |x| x['rows'] }==34560 && sessions.length==24 && groups.length==5760 && groups.values.all? { |x| x==6 } && endogenous_rows==11520
      {source_sha256:SHA,rows:34560,sessions:24,aggregate_only:true,endogenous_excluded:endogenous_rows,endogenous_payoff_adjustments:endogenous_adjusted,groups:counts.sort.to_h}
    end
  end
end
puts JSON.pretty_generate(RithmT16::SourceAudit.audit(ARGV.fetch(0))) if $PROGRAM_NAME==__FILE__
