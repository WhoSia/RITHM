# frozen_string_literal: true
require_relative 'online_actor_history'
require 'json'
module Rithm210LongitudinalIdentity
  module_function

  def audit(groups)
    individual=Hash.new{|h,k|h[k]=[]}
    group_members=Hash.new{|h,k|h[k]=Hash.new{|a,b|a[b]=[]}}
    groups.each do |(session,section,group,period),people|
      people.each do |r|
        id=r['ID'].to_i
        individual[[session,id]] << [section,period,group]
        group_members[[session,group]][section] << id if period==1
      end
    end
    raise 'wrong number of distinct participants' unless individual.size==288
    raise 'participant chronology incomplete' unless individual.values.all? do |history|
      history.size==117 && history.map{|sec,t,_|[sec,t]}.uniq.size==117 &&
        history.map{|_,_,g|g}.uniq.size==1
    end
    raise 'group assignment changed across sections' unless group_members.size==48 &&
      group_members.values.all? do |sections|
        sections.keys.sort==[2,3,4] && sections.values.map{|ids|ids.sort}.uniq.size==1 &&
          sections.values.all?{|ids|ids.uniq.size==6}
      end
    {sessions:individual.keys.map(&:first).uniq.size,participants:individual.size,
      sections_per_person:3,observations_per_person:117,
      groups:group_members.size,unchanged_group_compositions:group_members.size}
  end
end
if __FILE__==$PROGRAM_NAME
  puts JSON.pretty_generate(Rithm210LongitudinalIdentity.audit(Rithm210OnlineIdentity.source(ARGV.fetch(0))))
end
