# frozen_string_literal: true
# RITHM 2.8 P0-R7 — synthetic administrative demand / dropout / repair.
require 'json'
module RithmP0R7
 GROUPS=[:A,:B].freeze
 def self.simulate(policy:,friction:0,repair:false,rounds:8)
  pending=[];arrivals={A:0,B:0};served={A:0,B:0};dropped={A:0,B:0}
  repaired={A:0,B:0};waiting={A:0,B:0};previous=nil
  trace=[]
  rounds.times do |t|
   GROUPS.each{|g|pending<<[t,g];arrivals[g]+=1}
   pending.reject! do |birth,g|
    deadline=(g==:A ? 3 : 2)-(friction==0 ? 0 : 1)
    expired=t-birth>=deadline
    dropped[g]+=1 if expired
    expired
   end
   if repair&&t>0&&t%4==0
    GROUPS.each{|g|next unless dropped[g]>repaired[g]
     pending<<[t,g];arrivals[g]+=1;repaired[g]+=1}
   end
   choice=case policy
    when :fifo_a_tie then pending.min_by{|birth,g|[birth,g.to_s]}
    when :priority_a then pending.select{|_,g|g==:A}.min_by(&:first)||pending.min_by(&:first)
    when :priority_b then pending.select{|_,g|g==:B}.min_by(&:first)||pending.min_by(&:first)
    when :alternate then
     g=t.even? ? :A : :B
     pending.select{|_,x|x==g}.min_by(&:first)||pending.min_by(&:first)
    else raise ArgumentError,policy.to_s
   end
   available=choice&&!(friction==2&&previous&&previous!=choice[1])
   if available
    pending.delete_at(pending.index(choice));served[choice[1]]+=1
   end
   previous=choice[1] if choice
   pending.each{|_,g|waiting[g]+=1}
   GROUPS.each{|g|raise 'episode accounting failed' unless arrivals[g]==served[g]+dropped[g]+pending.count{|_,h|h==g}}
   trace<<[t,pending.length,served.dup,dropped.dup]
  end
  {policy:policy,friction:friction,repair:repair,arrivals:arrivals,served:served,
   dropped:dropped,waiting:waiting,reattempts:repaired,
   pending:GROUPS.to_h{|g|[g,pending.count{|_,h|h==g}]},trace:trace}
 end
end
if $PROGRAM_NAME==__FILE__
 x=[:fifo_a_tie,:priority_a,:priority_b,:alternate].product([0,1,2],[false,true]).map do |policy,friction,repair|
  RithmP0R7.simulate(policy:policy,friction:friction,repair:repair)
 end
 puts JSON.pretty_generate(x)
end
