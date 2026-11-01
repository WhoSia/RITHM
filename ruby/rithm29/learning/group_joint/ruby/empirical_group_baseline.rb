# frozen_string_literal: true
require 'csv'
require 'json'
module RithmEmpiricalBaseline
 module_function
 def read_rows(path)
  grouped = {}
  CSV.foreach(path, headers: true) do |r|
   s=r['session'].to_i; t=r['trt'].to_i; p=r['Period'].to_i
   next unless t.between?(1,3) && s!=2 && s!=101 && p.between?(1,39)
   key=[s,r['section'].to_i,r['Group'].to_i,p]
   (grouped[key] ||= []) << r
  end
  grouped.map do |key, a|
   raise 'invalid group size' unless a.size==6
   prev=a.first['NumA'].to_i
   up=a.sum{|r|r['switchBtoAWill'].to_i}
   down=a.sum{|r|r['switchAtoBWill'].to_i}
   raise 'invalid transition' unless up.between?(0,6-prev) && down.between?(0,prev) && prev+up-down==a.first['NumAnext'].to_i
   {session:key[0], trt:a.first['trt'].to_i, prev:prev, up:up, down:down, nex:prev+up-down}
  end
 end
 def fitted(rows)
  all=Hash.new(0); by=Hash.new{|h,k|h[k]=Hash.new(0)}
  rows.each{|r| k=[r[:up],r[:down]];all[k]+=1;by[[r[:trt],r[:prev]]][k]+=1}
  [all,by,rows.size]
 end
 def probabilities(model,trt,prev,conditional:,alpha:20.0)
  all,by,n=model
  support=(0..6-prev).flat_map{|u|(0..prev).map{|d|[u,d]}}
  # Global frequency prior, restricted to the feasible outcomes given prev.
  prior=support.to_h{|k|[k,(all[k]+1.0)/(n+support.size)]}
  total=prior.values.sum
  prior.transform_values!{|p|p/total}
  return prior unless conditional
  counts=by.fetch([trt,prev],{});m=counts.values.sum
  support.to_h{|k|[k,(counts.fetch(k,0)+alpha*prior[k])/(m+alpha)]}
 end
 def evaluate(path,alpha:20.0)
  data=read_rows(path);sessions=data.map{|r|r[:session]}.uniq.sort
  raise 'not 24 sessions' unless sessions.size==24 && data.size==5616
  folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
  rows=sessions.map do |s|
   test=data.select{|r|r[:session]==s}
   train=data.reject{|r|folds[r[:session]]==folds[s]}
   model=fitted(train)
   x={session:s,fold:folds[s],n:test.size}
   [false,true].each do |cond|
    kind=cond ? 'conditional' : 'global'
    joint=0.0;count=0.0
    test.each do |r|
     p=probabilities(model,r[:trt],r[:prev],conditional:cond,alpha:alpha)
     joint-=Math.log(p.fetch([r[:up],r[:down]]))
     count-=Math.log(p.sum{|(u,d),v|r[:prev]+u-d==r[:nex] ? v : 0.0})
    end
    x[kind]={joint:joint/test.size,count:count/test.size}
   end
   x
  end
  pooled=[:joint,:count].to_h{|h|[h,%w[global conditional].to_h{|k|[k,rows.sum{|r|r[:n]*r[k][h]}/data.size.to_f]}]}
  {observations:data.size,sessions:sessions.size,pooled:pooled,session_rows:rows}
 end
end
if __FILE__==$PROGRAM_NAME
 puts JSON.pretty_generate(RithmEmpiricalBaseline.evaluate(ARGV.fetch(0)))
end
