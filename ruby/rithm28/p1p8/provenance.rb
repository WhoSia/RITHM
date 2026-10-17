# frozen_string_literal: true
require_relative '../p1p7/receipt'
module RithmP1P8
 Record=Struct.new(:id,:published,:received,:trusted,:declared_id,keyword_init:true)
 class Contract
  attr_reader :records
  def initialize(h:,kind:)
   @h=h
   @records=Array.new(h){|i|Record.new(id:i,published:i+1,received:i+1,trusted:true,declared_id:i)}
   case kind
   when :clean then nil
   when :duplicate then @records<<@records.first.dup
   when :missing then @records.first.received=h+100
   when :untrusted then @records.each{|r|r.trusted=false}
   when :mislabel then @records.first.declared_id=h+10
   when :reorder then @records[0].received=4;@records[1].received=2
   when :conflict then @records<<Record.new(id:0,published:1,received:2,trusted:true,declared_id:1)
   else raise ArgumentError,kind.to_s
   end
   validate!
  end
  def validate!
   @records.each{|r|raise 'invalid timestamp' if r.published<r.id+1||r.received<r.published}
   raise 'conflicting trusted identity' if @records.group_by(&:id).any?{|_,a|a.select(&:trusted).map(&:declared_id).uniq.length>1}
  end
  def observation(t,world)
   @records.select{|r|r.trusted&&r.received==t&&r.id.between?(0,@h-1)&&r.declared_id==r.id}.uniq{|r|r.id}.map{|r|[r.id,world[r.id]]}.sort
  end
 end
 def self.minimum(h:,kind:)
  contract=Contract.new(h:h,kind:kind)
  (0..2).find{|b|RithmP1P7::Solver.new(h:h,budget:b,contract:contract).solve}
 end
end
if __FILE__==$PROGRAM_NAME
 [5,6].each{|h|[:clean,:duplicate,:missing,:untrusted,:mislabel,:reorder].each{|k|puts "H=#{h} kind=#{k} min=#{RithmP1P8.minimum(h:h,kind:k)}"}}
end