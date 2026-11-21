"""RITHM R66-T9. Exact serial-shock covariance and finite-horizon quadratic welfare.

Stylized aggregate linear response x[t+1]=rho*x[t]+epsilon*z[t], NOT a
six-person bounded-occupancy game or a fitted human behavioral law.
"""
from fractions import Fraction as Q

def welfare(horizon=40,rho=Q(1,2),eps=Q(1,5),mode="iid"):
    if not isinstance(horizon,int) or horizon<2 or abs(Q(rho))>1 or Q(eps)<0:
        raise ValueError("invalid horizon, rho or eps")
    rho,eps=Q(rho),Q(eps)
    if mode not in {"iid","common","alternating"}:
        raise ValueError("mode")
    if mode=="alternating":
        x=Q(0);total=Q(0)
        for t in range(horizon):
            total+=x*x
            if t<horizon-1:x=rho*x+eps*(-1)**t
        return total
    return sum(
        eps**2*(
            sum((rho**(2*j) for j in range(t)),Q(0)) if mode=="iid"
            else sum((rho**j for j in range(t)),Q(0))**2
        ) for t in range(horizon)
    )

def serial_covariance_bound(horizon,rho,eps,delta=1):
    """Exact upper bound if each cross-date E[z_s*z_r] differs by <=delta."""
    if not isinstance(horizon,int) or horizon<2 or abs(Q(rho))>1 or Q(eps)<0 or not 0<=Q(delta)<=2:
        raise ValueError("invalid arguments")
    rho,eps,delta=abs(Q(rho)),Q(eps),Q(delta)
    return 2*eps**2*delta*sum((sum((
        rho**(2*t-2-s-r) for s in range(t) for r in range(s+1,t)
    ),Q(0)) for t in range(2,horizon)),Q(0))

def iid_occupancy_differencing_null(n=6,p=Q(2,3)):
    """IID Binomial occupancy N_t -> Cov(delta N_t, delta N_t+1)=-Var(N)."""
    if not isinstance(n,int) or n<1 or not 0<=Q(p)<=1:raise ValueError("n,p")
    return -n*Q(p)*(1-Q(p))

if __name__=="__main__":
    for rho in (Q(1,2),Q(0),Q(-1,2)):
        print(rho,{k:round(float(welfare(rho=rho,mode=k)),9) for k in
              ("iid","common","alternating")})
