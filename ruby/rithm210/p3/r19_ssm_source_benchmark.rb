# frozen_string_literal: true
# Original 24-session source, prior-only exact SSMq choice Brier benchmark.
# No tuning/heldout model selection; no participant rows published.
require 'csv'
require 'digest'
require 'json'
require_relative 'r19_ssm_exact'
module Rithm210R19SSMSourceBenchmark
  module_function
  S=Rithm210R19SSMExact
  ORIGINAL_SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'
  def run(path,sessions:nil,q_values:[1,2,3],first_period:1,last_period:40)
    raise 'original human-source mismatch' unless Digest::SHA256.file(path).hexdigest==ORIGINAL_SHA
    raise ArgumentError,'q1..9 distinct required' unless q_values.is_a?(Array)&&q_values.uniq.size==q_values.size&&q_values.all?{|q|q.is_a?(Integer)&&q.between?(1,9)}
    raise ArgumentError,'period contract' unless first_period==1&&last_period==40
    all=[]
    CSV.foreach(path,headers:true) do |r|
      sid=r.fetch('session').to_i
      next if [2,101].include?(sid)||!r.fetch('trt').to_i.between?(1,3)
      next if sessions&&!sessions.include?(sid)
      next unless r.fetch('Period').to_i.between?(first_period,last_period)
      all<<r
    end
    raise 'no observations' if all.empty?
    all.sort_by!{|r|[r.fetch('session').to_i,r.fetch('section').to_i,r.fetch('Period').to_i,r.fetch('ID').to_i]}
    histories={}
    aggregates=Hash.new{|h,k|h[k]={count:0,brier:0.0}}
    per_session=Hash.new{|h,k|h[k]={count:0,brier:0.0}}
    all.each do |r|
      sid=r.fetch('session').to_i;section=r.fetch('section').to_i
      id=r.fetch('ID').to_i;t=r.fetch('Period').to_i
      trt=r.fetch('trt').to_i
      hist=histories[[sid,section,id]]||=S.blank_history
      previous=hist.fetch(:route_count,0)
      raise 'actor history discontinuity' unless previous==t-1
      informed=r.fetch('Informed')=='1'
      outcome=r.fetch('RouteA').to_i
      raise 'nonbinary route' unless [0,1].include?(outcome)
      probabilities=q_values.to_h do |q|
        ["ssm_#{q}",S.probability(history:hist,q:q,informed:informed).to_f]
      end
      probabilities['own_route_frequency']=(hist.fetch(:a_choices,0)+1).to_f/(previous+2)
      probabilities.each do |label,p|
        a=aggregates[[trt,informed,label]]
        a[:count]+=1;a[:brier]+=(outcome-p)**2
        b=per_session[[sid,trt,informed,label]]
        b[:count]+=1;b[:brier]+=(outcome-p)**2
      end
      profit10=Rational(r.fetch('profit'))*10
      raise 'profit precision unsupported' unless profit10.denominator==1
      # Uninformed branch never receives NumA, even as an accidental feature.
      S.append(history:hist,route_a:outcome==1,informed:informed,
        payoff_tenths:profit10.to_i,num_a:informed ? r.fetch('NumA').to_i : nil)
      hist[:route_count]=previous+1
      hist[:a_choices]=hist.fetch(:a_choices,0)+outcome
    end
    {sessions:all.map{|r|r.fetch('session').to_i}.uniq.size,individual_periods:all.size,
      q_values:q_values,
      scope:'Exploratory, same source, fixed-q trial sampling with symmetric ties; not author full persistent-q latent fit or autonomous group welfare.',
      by_treatment_information_model:aggregates.sort_by{|key,_|key.map(&:to_s)}.map do |(trt,inf,name),x|
        {treatment:trt,informed:inf,model:name,n:x[:count],brier:x[:brier]/x[:count]}
      end,
      session_scores:per_session.sort_by{|key,_|key.map(&:to_s)}.map do |(sid,trt,inf,name),x|
        {session:sid,treatment:trt,informed:inf,model:name,n:x[:count],brier:x[:brier]/x[:count]}
      end}
  end
end
if __FILE__==$PROGRAM_NAME
  puts JSON.pretty_generate(Rithm210R19SSMSourceBenchmark.run(ARGV.fetch(0),
    sessions:ARGV[1] ? ARGV[1].split(',').map(&:to_i) : nil))
end
