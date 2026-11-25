# frozen_string_literal: true
require_relative 'r66_t20_dynamic'
module RithmT20
  # Exact independent mixed Nash classification by (pure A,pure B,mixed) counts
  # within each old-route type. One-mixer continua have affine row/revision cost;
  # endpoints suffice for any linear Bellman objective. No correlated equilibria.
  module AllMixed
    module_function
    def counts(n)
      (0..n).flat_map { |a| (0..n-a).map { |b| [a,b,n-a-b] } }
    end
    def profile_pairs(n,kappa)
      k=Rational(kappa);raise ArgumentError,'state/friction' unless n.is_a?(Integer) && n.between?(0,6) && k>=0
      theta=[(11+k)/3,(11-k)/3]
      counts(n).product(counts(6-n)).flat_map do |groups|
        pure_a=groups.sum { |a,b,m| a }; m=groups.sum { |a,b,m| m }
        if m==1
          i=groups.index { |a,b,m| m==1 }; next [] unless pure_a==theta[i]
          lo=Rational(pure_a);hi=lo+1
          groups.each_with_index do |(a,b,_),j|
            lo=[lo,theta[j]].max if b>0
            hi=[hi,theta[j]+1].min if a>0
          end
          sums=lo<=hi ? [lo,hi].uniq : []
        else
          sums=[Rational(pure_a-groups.each_with_index.sum { |(_,_,m),j| m*theta[j] },1-m)]
        end
        sums.filter_map do |s|
          next unless groups.each_with_index.all? do |(a,b,m),j|
            (a==0 || s-1<=theta[j]) && (b==0 || s>=theta[j]) && (m==0 || (s-theta[j]).between?(0,1))
          end
          p=groups.each_with_index.map { |(a,b,m),j| Array.new(a,Rational(1))+Array.new(b,Rational(0))+Array.new(m,s-theta[j]) }
          p
        end
      end.uniq
    end
    def row(pairs)
      q=Array.new(7,Rational(0));q[0]=1
      pairs.flatten.each_with_index do |p,i|
        (i+1).downto(0) { |j| q[j]=(1-p)*q[j]+(j==0 ? 0 : p*q[j-1]) }
      end
      s=pairs[0].sum { |p| 1-p }+pairs[1].sum
      raise 'mass' unless q.sum==1
      [q,s]
    end
    def actions(n,k)
      profile_pairs(n,k).map { |p| row(p) }.uniq
    end
    def bounds(horizon:,kappa:,resource:0,opportunity:Rational(1,2))
      k,c,p=[kappa,resource,opportunity].map { |v| Rational(v) }
      raise ArgumentError,'parameters' unless horizon.is_a?(Integer) && horizon>=1 && c>=0 && p.between?(0,1)
      acts=(0..6).map { |n| actions(n,k) }; g=(0..6).map { |n| 3*(n-4)**2 };lo=g.dup;hi=g.dup
      (horizon-1).times do
        lo,hi=[lo,hi].each_with_index.map do |v,side|
          g.each_with_index.map do |cost,n|
            vals=acts[n].map { |row,s| row.zip(v).sum { |q,x| q*x }+c*s }
            cost+(1-p)*v[n]+p*(side==0 ? vals.min : vals.max)
          end
        end
      end
      {lo:lo,hi:hi,action_counts:acts.map(&:size)}
    end
  end
end
