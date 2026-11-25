# frozen_string_literal: true
# Restricted equilibrium-selection envelope: all labelled pure and old-route-symmetric
# independent mixed stage Nash equilibria, common active opportunity, kappa in [0,2].
module RithmT20
  module Dynamic
    module_function
    def gains(n,a,b,k)
      [3*((n-1)*(1-a)+(6-n)*b)-11-k,11-3*(n*(1-a)+(5-n)*b)-k]
    end
    def br?(p,g)
      p==0 ? g<=0 : p==1 ? g>=0 : g==0
    end
    def symmetric(n,kappa)
      k=Rational(kappa);raise ArgumentError,'state/friction' unless n.is_a?(Integer) && n.between?(0,6) && k.between?(0,2)
      return [[0,((11-k)/15).clamp(0,1)]] if n==0
      return [[((4-k)/15).clamp(0,1),0]] if n==6
      eq=[]
      [0,1,:mix].product([0,1,:mix]).each do |a,b|
        if a==:mix && b==:mix
          # solve 2x2 exact linear gain equations
          c,d=gains(n,0,0,k); u=-3*(n-1);v=3*(6-n); w=3*n;x=-3*(5-n);det=u*x-v*w
          a=Rational(-c*x+v*d,det);b=Rational(-u*d+w*c,det)
        elsif a==:mix
          s=-3*(n-1); c=gains(n,0,b,k)[0]
          if s==0
            raise 'continuum unsupported' if c==0
            next
          end
          a=Rational(-c,s)
        elsif b==:mix
          s=-3*(5-n);c=gains(n,a,0,k)[1]
          if s==0
            raise 'continuum unsupported' if c==0
            next
          end
          b=Rational(-c,s)
        end
        next unless a.between?(0,1) && b.between?(0,1)
        eq<<[a,b] if gains(n,a,b,k).zip([a,b]).all? { |g,p| br?(p,g) }
      end
      eq.map { |a,b| [Rational(a),Rational(b)] }.uniq
    end
    def pure(n,k)
      (0...64).filter_map do |mask|
        nn=6.times.count { |i| mask[i]==1 }
        ok=6.times.all? do |i|
          old=i<n;cur=mask[i]==1;other=nn-(cur ? 1 : 0)
          ca=other+1+(old ? 0 : k);cb=2*(6-other)+(old ? k : 0)
          cur ? ca<=cb : cb<=ca
        end
        next unless ok
        s=6.times.count { |i| (mask[i]==1)!=(i<n) }
        [Array.new(7){|j| Rational(j==nn ? 1 : 0)},Rational(s)]
      end.uniq
    end
    def mixed_row(n,a,b)
      p=Array.new(7,Rational(0));s=0
      64.times do |mask|
        nn=n;w=Rational(1);moves=0
        6.times do |i|
          r=i<n ? a : b
          if mask[i]==1
            w*=r;nn+=i<n ? -1 : 1;moves+=1
          else
            w*=1-r
          end
        end
        p[nn]+=w;s+=w*moves
      end
      raise 'mass' unless p.sum==1 && s==n*a+(6-n)*b
      [p,s]
    end
    def actions(n,k)
      (pure(n,k)+symmetric(n,k).map { |a,b| mixed_row(n,a,b) }).uniq
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
