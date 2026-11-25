# frozen_string_literal: true
module RithmT25
  module TwoProxy
    module_function
    # Tag order 00,01,10,11. Switch S=1 implies latent reconsideration E=1.
    def product(a,b)
      a,b=[a,b].map{|x|Rational(x)};raise ArgumentError,'probability' unless [a,b].all?{|x|x.between?(0,1)}
      [(1-a)*(1-b),(1-a)*b,a*(1-b),a*b]
    end
    def det(x);x[0]*x[3]-x[1]*x[2];end
    def observed(j0,j1)
      a,b=[j0,j1].map{|r|r.map{|v|Rational(v)}}
      raise ArgumentError,'joint rows' unless [a,b].all?{|r|r.size==4 && r.all?{|x|x>=0}} && a.sum+b.sum==1 && b.sum>0
      s=b.sum;r=a.zip(b).map(&:sum);active=b.map{|x|x/s}
      [s,r,active]
    end
    # S independent of the joint tags given E; tags need not be mutually independent.
    def witness(j0,j1,q)
      s,r,a=observed(j0,j1);q=Rational(q)
      raise ArgumentError,'opportunity rate' unless q.between?(s,1)
      b=q==1 ? a : r.zip(a).map{|x,y|(x-q*y)/(1-q)}
      raise ArgumentError,'infeasible' unless b.all?{|x|x>=0} && (q!=1 || r==a)
      {q:q,response:s/q,active:a,inactive:b,active_covariance:det(a),inactive_covariance:det(b)}
    end
    def identify(j0,j1)
      s,r,a=observed(j0,j1);raise ArgumentError,'active tag dependence' unless det(a)==0
      d=det(r);c=r[0]*a[3]+r[3]*a[0]-r[1]*a[2]-r[2]*a[1]
      if c==0
        raise ArgumentError,'incompatible independence' unless d==0
        h=a.each_index.filter_map{|i|r[i]/a[i] if a[i]>0}.min
        return {status: :set,q_low:s,q_high:[1,h].min}
      end
      w=witness(j0,j1,d/c);raise ArgumentError,'inactive tag dependence' unless w[:inactive_covariance]==0
      w.merge(status: :point)
    end
    def joint(q,p,a,b)
      q,p=[q,p].map{|x|Rational(x)}
      raise ArgumentError,'probabilities' unless [q,p].all?{|x|x.between?(0,1)} && [a,b].all?{|x|x.size==4 && x.sum==1 && x.all?{|v|v>=0}}
      [a.zip(b).map{|x,y|q*(1-p)*x+(1-q)*y},a.map{|x|q*p*x}]
    end
  end
end
