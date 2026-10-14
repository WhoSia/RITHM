# frozen_string_literal: true
# RITHM 2.8 P0-R3, Ruby FIRST. 5-minute periods, all queues in vehicles.
class QueueCourt
  attr_reader :states,:edges,:unsafe
  def initialize(delay:,policy:,k:3,b:1,cap:3)
    @delay,@policy,@k,@b,@cap=delay,policy,k,b,cap
    @states=[];@edges=[];@ids={};@unsafe=false
    [0,1].each{|active| add([0,0,active,0,0,0])}
    i=0
    while i<@states.size
      q0,q1,active,prev,h,mem=@states[i]
      command,nextmem=choose(prev,mem)
      effective=delay ? active : command
      @edges[i]=[]
      [0,1,2].each do |w|
        event=w==0 ? 0 : 1
        next if h.to_s(2).count('1')+event>b
        nq0=[0,q0+(w==1 ? 1 : 0)-(effective==0 ? 1 : 0)].max
        nq1=[0,q1+(w==2 ? 1 : 0)-(effective==1 ? 1 : 0)].max
        overflow=nq0>cap||nq1>cap
        @unsafe||=overflow||nq0+nq1>2
        nq0=[nq0,cap].min;nq1=[nq1,cap].min
        nh=k>1 ? (((h<<1)|event)&((1<<(k-1))-1)) : 0
        j=add([nq0,nq1,command,w,nh,nextmem])
        cost=4*(nq0+nq1)+(command==active ? 0 : 1)
        @edges[i]<<[j,cost]
      end
      i+=1
    end
  end
  def add(s)
    return @ids[s] if @ids.key?(s)
    i=@states.size;@ids[s]=i;@states<<s;@edges<<[];i
  end
  def choose(prev,mem)
    case @policy
    when :fixed0 then [0,mem]
    when :fixed1 then [1,mem]
    when :last_shock then [prev==2 ? 1 : 0,mem]
    when :parity then [mem,1-mem]
    when :sticky then [prev==0 ? mem : prev-1,prev==0 ? mem : prev-1]
    else raise ArgumentError,"unknown policy"
    end
  end
  # Karp maximum reachable cycle mean (cost stored at 4x exact integer scale).
  def maximum_cycle_mean
    n=@states.size
    prior=Array.new(n,0);dp=[prior]
    n.times do
      cur=Array.new(n,-Float::INFINITY)
      @edges.each_with_index{|es,u|es.each{|v,c|cur[v]=[cur[v],prior[u]+c].max}}
      dp<<cur;prior=cur
    end
    (0...n).map do |v|
      next -Float::INFINITY unless dp[n][v].finite?
      (0...n).filter_map{|t|(dp[n][v]-dp[t][v]).fdiv(n-t) if dp[t][v].finite?}.min
    end.max/4.0
  end
end
if $PROGRAM_NAME==__FILE__
  [:fixed0,:fixed1,:last_shock,:parity,:sticky].each do |policy|
    [false,true].each do |delay|
      c=QueueCourt.new(delay:delay,policy:policy)
      puts [policy,delay,c.states.size,c.maximum_cycle_mean.round(8),c.unsafe].join(',')
    end
  end
end
