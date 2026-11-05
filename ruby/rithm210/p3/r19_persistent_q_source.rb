# frozen_string_literal: true
# Original CSV, fixed latent q_i Bayesian posterior, per-section history.
# Exploratory pooled Brier scores: no heldout model selection or causal claim.
require 'csv'
require 'digest'
require 'json'
require_relative 'r19_ssm_source_benchmark'
require_relative 'r19_persistent_q_filter'
module Rithm210R19PersistentQSource
  module_function
  S=Rithm210R19SSMExact
  F=Rithm210R19PersistentQFilter::Filter
  SOURCE_SHA=Rithm210R19SSMSourceBenchmark::ORIGINAL_SHA
  def run(csv,selected_sessions:nil,qmax:3,lapse:0.02)
    raise 'original SHA mismatch' unless Digest::SHA256.file(csv).hexdigest==SOURCE_SHA
    raise ArgumentError,'qmax1..9' unless qmax.is_a?(Integer)&&qmax.between?(1,9)
    raw=[]
    CSV.foreach(csv,headers:true) do |r|
      sid=r.fetch('session').to_i
      next if [2,101].include?(sid)||!r.fetch('trt').to_i.between?(1,3)
      next if selected_sessions&&!selected_sessions.include?(sid)
      raw<<r if r.fetch('Period').to_i.between?(1,40)
    end
    raise 'empty selection' if raw.empty?
    raw.sort_by!{|r|[r.fetch('session').to_i,r.fetch('section').to_i,r.fetch('Period').to_i,r.fetch('ID').to_i]}
    histories={};posteriors={}
    aggregate=Hash.new{|h,k|h[k]=[0,0.0]}
    raw.each do |r|
      sid=r.fetch('session').to_i;sec=r.fetch('section').to_i;id=r.fetch('ID').to_i
      key=[sid,sec,id]
      hist=histories[key]||=S.blank_history
      filt=posteriors[key]||=F.new(qmax:qmax,lapse:lapse)
      period=r.fetch('Period').to_i
      prior_count=hist.fetch(:n,0)
      raise 'actor trial nonconsecutive' unless prior_count==period-1
      inf=r.fetch('Informed')=='1'
      y=r.fetch('RouteA').to_i
      raise 'binary route required' unless [0,1].include?(y)
      persistent=filt.predict(history:hist,informed:inf)
      # Share EXACT q-probability computations; no second convolution.
      uniform=filt.last_probabilities.sum/qmax.to_f
      own=(hist.fetch(:route_a_count,0)+1).to_f/(prior_count+2)
      {persistent:persistent,uniform_prior:uniform,own_route_frequency:own}.each do |label,p|
        x=aggregate[[r.fetch('trt').to_i,inf,label]]
        x[0]+=1;x[1]+=(y-p)**2
      end
      filt.update(route_a:y==1)
      payoff10=Rational(r.fetch('profit'))*10
      raise 'profit tenths required' unless payoff10.denominator==1
      S.append(history:hist,route_a:y==1,informed:inf,payoff_tenths:payoff10.to_i,
        num_a:inf ? r.fetch('NumA').to_i : nil)
      hist[:n]=prior_count+1
      hist[:route_a_count]=hist.fetch(:route_a_count,0)+y
    end
    {sessions:raw.map{|r|r.fetch('session').to_i}.uniq.size,individual_periods:raw.size,
     qmax:qmax,lapse:lapse,
     caution:'Within-section fixed actor q_i posterior, declared lapse and fair ties; not across-segment memory or original authors full simulation.',
     results:aggregate.sort_by{|key,_|key.map(&:to_s)}.map do |(trt,inf,label),(n,sum)|
       {treatment:trt,informed:inf,model:label,n:n,brier:sum/n}
     end}
  end
end
if __FILE__==$PROGRAM_NAME
  puts JSON.pretty_generate(Rithm210R19PersistentQSource.run(ARGV.fetch(0),
    selected_sessions:ARGV[1] ? ARGV[1].split(',').map(&:to_i) : nil))
end
