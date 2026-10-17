# frozen_string_literal: true
require 'json'
# Synthetic-only 2-person service/outage game; assumed revocable source authority.
# Does not attest real source identity, beneficiary delivery, or causal welfare.
module RithmDynamic
  SCHEMA='rithm.p1p18.revocation_game.v1'
  module_function
  def validate!(c)
    %w[horizon budget probe_cost delay revoke_at restore_at].each{|k|raise ArgumentError,k unless c[k].is_a?(Integer)}
    h=c.fetch('horizon')
    raise ArgumentError,'bounds' unless h.between?(1,7)&&c['budget'].between?(0,4)&&c['probe_cost'].between?(0,2)&&c['delay'].between?(1,h)&&c['revoke_at'].between?(0,h+1)&&c['restore_at'].between?(c['revoke_at'],h+1)
  end
  def root(c)
    [0,(0..c.fetch('horizon')).map{|world|[world,0,0]},2,0,0,[]]
  end
  def key(s);JSON.generate(s);end
  def trust_at(c,receipt)
    receipt<c['revoke_at']||receipt>=c['restore_at']
  end
  def actions(c,s)
    spent=s[4];result=[]
    2.times{|person|2.times{|boost|2.times{|probe|result<<[person,boost,probe] if spent+boost+probe*c['probe_cost']<=c['budget']}}}
    result
  end
  def outcomes(c,s,action)
    t,rows,last,setup,spent,probes=s
    raise ArgumentError,'invalid action' unless actions(c,s).include?(action)
    raise ArgumentError,'terminal' if t>=c['horizon']
    person,boost,probe=action
    switching=last!=2&&last!=person
    next_setup=setup|(switching ? 1 : 0)
    next_probes=probes+(probe==1 ? [t] : [])
    event=t+1-c['delay']
    usable=event>=0&&next_probes.include?(event)&&trust_at(c,t+1)
    groups={}
    rows.each do |world,a,b|
      outage=world==t+1 ? 1 : 0
      cap=[0,1+boost-outage-(switching&&setup==0 ? 1 : 0)].max
      aa,bb=person==0 ? [[2,a+cap].min,b] : [a,[2,b+cap].min]
      observation=usable ? (world==event+1 ? 1 : 0) : 2
      (groups[observation]||=[])<<[world,aa,bb]
    end
    groups.sort_by{|ob,_|ob}.map do |ob,nrows|
      [ob,[t+1,nrows,person,next_setup,spent+boost+probe*c['probe_cost'],next_probes]]
    end
  end
  def terminal_win(s,c)
    s[0]==c['horizon']&&s[1].all?{|_world,a,b|a==2&&b==2}
  end
  def synthesize(c)
    validate!(c)
    memo={};decisions={}
    rec=nil
    rec=lambda do |s|
      return terminal_win(s,c) if s[0]==c['horizon']
      k=key(s)
      return memo.fetch(k) if memo.key?(k)
      counters=[]
      actions(c,s).each do |action|
        children=outcomes(c,s,action)
        bad=children.find{|_ob,next_s|!rec.call(next_s)}
        if bad.nil?
          decisions[k]={'action'=>action,'children'=>children.map{|ob,next_s|{'observation'=>ob,'key'=>key(next_s)}}}
          return memo[k]=true
        end
        counters<<{'action'=>action,'observation'=>bad[0],'key'=>key(bad[1])}
      end
      decisions[k]={'counterexamples'=>counters}
      memo[k]=false
    end
    first=root(c);winning=rec.call(first);nodes={}
    visit=nil
    visit=lambda do |s|
      return if s[0]==c['horizon']
      k=key(s);return if nodes.key?(k)
      node=decisions.fetch(k);nodes[k]=node
      if winning
        outcomes(c,s,node.fetch('action')).each{|_ob,next_s|visit.call(next_s)}
      else
        node.fetch('counterexamples').each do |ce|
          successor=outcomes(c,s,ce.fetch('action')).find{|ob,next_s|ob==ce.fetch('observation')&&key(next_s)==ce.fetch('key')}
          raise 'invalid witness' unless successor
          visit.call(successor[1])
        end
      end
    end
    visit.call(first)
    {'schema'=>SCHEMA,'config'=>c,'certificate_type'=>winning ? 'winning' : 'losing',
     'root'=>key(first),'nodes'=>nodes,'synthetic_only'=>true,'real_world_welfare_verified'=>false}
  end
end
if __FILE__==$PROGRAM_NAME
  raise 'usage: ruby dynamic.rb CONFIG_JSON OUTPUT_JSON' unless ARGV.length==2
  config=JSON.parse(File.read(ARGV[0]))
  certificate=RithmDynamic.synthesize(config)
  File.write(ARGV[1],JSON.pretty_generate(certificate))
  warn "Ruby #{certificate.fetch('certificate_type')} certificate #{certificate.fetch('nodes').size} nodes"
end
