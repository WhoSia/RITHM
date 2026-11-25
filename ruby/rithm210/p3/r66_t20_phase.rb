# frozen_string_literal: true
require_relative 'r66_t20_all_mixed'
module RithmT20
  # Affine feasibility audit for every >=2-mixer pattern on kappa in [0,2].
  module Phase
    module_function
    def intervals(n)
      raise ArgumentError,'state' unless [4,5].include?(n)
      AllMixed.counts(n).product(AllMixed.counts(6-n)).filter_map do |groups|
        m=groups.sum { |a,b,r| r }; next if m<2
        pa=groups.sum { |a,b,r| a }; s=Rational(pa-Rational(11,3)*m,1-m)
        d=Rational(-Rational(groups[0][2]-groups[1][2],3),1-m)
        lo=Rational(0);hi=Rational(2);ok=true; terms=[]
        groups.each_with_index do |(a,b,r),i|
          q=s-Rational(11,3); t=d-(i==0 ? Rational(1,3) : -Rational(1,3));terms<<[q,t,r]
          constraints=[];constraints<<[1-q,-t] if a>0 || r>0;constraints<<[q,t] if b>0 || r>0
          constraints.each do |c,z|
            if z>0 then lo=[lo,-c/z].max
            elsif z<0 then hi=[hi,-c/z].min
            elsif c<0 then ok=false
            end
          end
        end
        next unless ok && lo<=hi
        # A genuine mixed player exists at some point iff its affine p is interior
        # at the midpoint, or at the singleton interval point.
        mid=(lo+hi)/2
        next unless terms.any? { |q,t,r| r>0 && (q+t*mid)>0 && (q+t*mid)<1 }
        {groups:groups,lo:lo,hi:hi}
      end
    end
    def witness(n,kappa)
      k=Rational(kappa);raise ArgumentError,'state/friction' unless [4,5].include?(n) && k.between?(0,Rational(4,3))
      if n==4
        [[1,1,Rational(5-3*k,9),Rational(5-3*k,9)],[Rational(5+3*k,9),Rational(5+3*k,9)]]
      else
        [[1,1,1,Rational(2-k,6),Rational(2-k,6)],[Rational(2+3*k,6)]]
      end
    end
  end
end
