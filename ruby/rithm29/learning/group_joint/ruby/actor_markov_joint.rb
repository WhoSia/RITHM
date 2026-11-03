# frozen_string_literal: true
require 'csv'
require 'json'
module RithmActorMarkov
 module_function
 def key(r); [r['trt'].to_i,r['Informed'].to_i,r['RouteA'].to_i,r['Cost'].to_f]; end
 def convolve(probs)
   probs.reduce([1.0]) do |q,p|
     z=Array.new(q.length+1,0.0)
     q.each_with_index{|v,i|z[i]+=v*(1-p);z[i+1]+=v*p};z
   end
 end
 def read_groups(path)
  groups=Hash.new{|h,k|h[k]=[]}
  CSV.foreach(path,headers:true) do |r|
   s=r['session'].to_i;t=r['trt'].to_i;p=r['Period'].to_i
   next unless t.between?(1,3) && s!=2 && s!=101 && p.between?(1,39)
   groups[[s,r['section'].to_i,r['Group'].to_i,p]] << r
  end
  sessions=groups.keys.map(&:first).uniq
  raise 'source mismatch' unless groups.length==5616 && sessions.length==24 && groups.values.all?{|a|a.length==6}
  groups
 end
 def trained(groups,folds,heldout_fold)
  counts=Hash.new{|h,k|h[k]=[0,0]}
  back=Hash.new{|h,k|h[k]=[0,0]}
  groups.each do |key,a|
   next if folds.fetch(key[0])==heldout_fold
   a.each do |r|
    y=r['switchWill'].to_i
    raise 'invalid label' unless [0,1].include?(y)
    counts[key(r)][0]+=y;counts[key(r)][1]+=1
    back[r['RouteA'].to_i][0]+=y;back[r['RouteA'].to_i][1]+=1
   end
  end
  [counts,back]
 end
 def p_switch(fit,r,alpha:20.0)
  counts,back=fit
  local=counts.fetch(key(r),[0,0])
  base=back.fetch(r['RouteA'].to_i,[0,0])
  prior=(base[0]+1.0)/(base[1]+2.0)
  (local[0]+alpha*prior)/(local[1]+alpha)
 end
 def binomial_convolution(probs);convolve(probs);end
 def run(path)
  groups=Hash.new{|h,k|h[k]=[]}
  CSV.foreach(path,headers:true) do |r|
   s=r['session'].to_i;t=r['trt'].to_i;p=r['Period'].to_i
   next unless t.between?(1,3)&&s!=2&&s!=101&&p.between?(1,39)
   groups[[s,r['section'].to_i,r['Group'].to_i,p]]<<r
  end
  sessions=groups.keys.map(&:first).uniq.sort
  raise 'source mismatch' unless groups.length==5616&&sessions.length==24&&groups.values.all?{|a|a.length==6}
  folds=sessions.each_with_index.to_h{|s,i|[s,i%6]}
  losses=[]
  6.times do |fold|
   counts=Hash.new{|h,k|h[k]=[0,0]};back=Hash.new{|h,k|h[k]=[0,0]}
   groups.each do |(s,*),a|
    next if folds[s]==fold
    a.each do |r|
     y=r['switchWill'].to_i
     raise 'invalid label' unless [0,1].include?(y)
     counts[key(r)][0]+=y;counts[key(r)][1]+=1
     back[r['RouteA'].to_i][0]+=y;back[r['RouteA'].to_i][1]+=1
    end
   end
   groups.each do |(s,*),a|
    next unless folds[s]==fold
    pred=->(r){
     k=counts.fetch(key(r),[0,0]);g=back.fetch(r['RouteA'].to_i,[0,0])
     prior=(g[0]+1.0)/(g[1]+2.0)
     (k[0]+20.0*prior)/(k[1]+20.0)
    }
    down=convolve(a.select{|r|r['RouteA'].to_i==1}.map(&pred))
    up=convolve(a.select{|r|r['RouteA'].to_i==0}.map(&pred))
    u=a.sum{|r|r['switchBtoAWill'].to_i}
    d=a.sum{|r|r['switchAtoBWill'].to_i}
    observed=up.fetch(u)*down.fetch(d)
    next_count=0.0
    up.each_with_index{|pu,i|down.each_with_index{|pd,j|next_count+=pu*pd if i-j==u-d}}
    raise 'nonpositive probability' if observed<=0||next_count<=0
    losses<<{session:s,joint:-Math.log(observed),count:-Math.log(next_count)}
   end
  end
  {n:losses.length,sessions:sessions.length,joint:losses.sum{|r|r[:joint]}/losses.size,
   count:losses.sum{|r|r[:count]}/losses.size}
 end
end
puts JSON.pretty_generate(RithmActorMarkov.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
