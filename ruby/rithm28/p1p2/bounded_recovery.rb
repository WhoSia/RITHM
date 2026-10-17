module BoundedRecovery
 def self.worst(r,d,phase=:off)
  case phase
  when :off then 1+worst(r,d,:on)
  when :on
   a=1+worst(r,d,:ordered)
   r>0 ? [a,1+worst(r-1,d,:off)].max : a
  when :ordered then d>0 ? 1+worst(r,d-1,:ordered) : 1
  else raise ArgumentError
  end
 end
 def self.formula(r,d);2*(r+1)+d+1;end
end
if __FILE__==$PROGRAM_NAME
 [[0,0],[1,0],[2,1],[3,2]].each{|r,d|raise unless BoundedRecovery.worst(r,d)==BoundedRecovery.formula(r,d)}
 puts 'P1-P2 four bounds verified'
end
