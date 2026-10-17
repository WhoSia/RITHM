# frozen_string_literal: true
require 'set'
module RithmP1P1
  Edge=Struct.new(:to,:action,keyword_init:true)
  class Game
    attr_reader :graph
    def initialize
      @graph={
        off:[Edge.new(to: :on,action: :clock)],
        on:[Edge.new(to: :off,action: :defer),Edge.new(to: :ordered,action: :authorized_review)],
        ordered:[Edge.new(to: :ordered,action: :defer),Edge.new(to: :restored,action: :confirmed_delivery)],
        restored:[Edge.new(to: :restored,action: :stay)]}
    end
    def reachable
      seen=Set[:off];todo=[:off]
      until todo.empty?
        s=todo.shift
        @graph.fetch(s).each{|e|unless seen.include?(e.to);seen.add(e.to);todo<<e.to;end}
      end
      seen
    end
    def connected?(nodes)
      ns=nodes.to_set
      nodes.all?{|start|
        seen=Set[start];todo=[start]
        until todo.empty?
          @graph.fetch(todo.pop).each{|e|if ns.include?(e.to)&&!seen.include?(e.to);seen.add(e.to);todo<<e.to;end}
        end
        seen==ns
      }
    end
    def fair_nonrestored(kind)
      raise ArgumentError unless [:weak,:strong].include?(kind)
      states=reachable.to_a.reject{|s|s==:restored}
      (1...(1<<states.length)).filter_map{|mask|
        nodes=states.each_with_index.filter_map{|s,i|s if mask&(1<<i)!=0}
        ns=nodes.to_set
        internal=nodes.flat_map{|s|@graph.fetch(s).filter_map{|e|[s,e] if ns.include?(e.to)}}
        next if internal.empty?||!connected?(nodes)
        next if nodes.length==1&&internal.none?{|s,e|s==e.to}
        fair=[:authorized_review,:confirmed_delivery].all?{|act|
          enabled=nodes.count{|s|@graph.fetch(s).any?{|e|e.action==act}}
          required=kind==:weak ? enabled==nodes.length : enabled>0
          !required||internal.any?{|_,e|e.action==act}}
        {states:nodes.sort,actions:internal.map{|_,e|e.action}.uniq.sort} if fair
      }
    end
    def identity_counterexample
      # Count-only projection does not preserve pending(B2).
      a={pending:1,served:1,dropped:1,eligible:1,owner:'B2'}
      b=a.merge(owner:'A2')
      {same_counts:[:pending,:served,:dropped,:eligible].all?{|k|a[k]==b[k]},pending_b2:[a[:owner]=='B2',b[:owner]=='B2']}
    end
  end
end
if __FILE__==$PROGRAM_NAME
 g=RithmP1P1::Game.new
 p weak:g.fair_nonrestored(:weak),strong:g.fair_nonrestored(:strong),identity:g.identity_counterexample
end