# frozen_string_literal: true
# Original-source group transition and sixfold contract. Ruby standard library only.
require 'csv'
require 'json'
require 'digest'
module RithmFoldContract
 module_function
 def run(path)
  groups=Hash.new { |h,k| h[k]=[] }
  CSV.foreach(path,headers:true) do |r|
   s=r.fetch('session').to_i;t=r.fetch('trt').to_i;p=r.fetch('Period').to_i
   next unless t.between?(1,3) && s!=2 && s!=101 && p.between?(1,39)
   key=[s,r.fetch('section').to_i,r.fetch('Group').to_i,p]
   groups[key] << r
  end
  raise 'unexpected group-period count' unless groups.size==5616
  sessions=groups.keys.map(&:first).uniq.sort
  raise 'unexpected session count' unless sessions.size==24
  folds=sessions.each_with_index.to_h{|s,i| [s,i%6]}
  n=Hash.new(0);strata=Hash.new(0)
  groups.each do |(s,_section,_g,_p),rows|
   raise 'invalid six-person group' unless rows.size==6
   n[s]+=1
   trts=rows.map{|r|r.fetch('trt')}.uniq
   prevs=rows.map{|r|r.fetch('NumA')}.uniq
   nexts=rows.map{|r|r.fetch('NumAnext')}.uniq
   raise 'inconsistent group state' unless trts.size==1 && prevs.size==1 && nexts.size==1
   a=prevs.first.to_i;b=nexts.first.to_i
   u=rows.sum{|r|r.fetch('switchBtoAWill').to_i}
   d=rows.sum{|r|r.fetch('switchAtoBWill').to_i}
   raise 'transition identity broken' unless a+u-d==b
   raise 'invalid info binary' unless rows.all?{|r| ['0','1'].include?(r.fetch('Informed'))}
   strata[[trts.first.to_i,rows.count{|r|r.fetch('Informed')=='1'}]]+=1
  end
  {source_sha256:Digest::SHA256.file(path).hexdigest,group_transitions:groups.size,
   person_transitions:groups.size*6,sessions:sessions.size,
   session_fold:sessions.map{|s|{session:s,fold:folds[s],transitions:n[s]}},
   fold_counts:(0...6).to_h{|f|[f,n.select{|s,_|folds[s]==f}.values.sum]},
   information_strata:strata.sort.map{|(t,i),v|{trt:t,informed_per_group:i,transitions:v}}}
 end
end
puts JSON.pretty_generate(RithmFoldContract.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
