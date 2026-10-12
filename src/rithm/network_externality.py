"""P17 exact STATIC separable congestion externality accounting.

Pure mathematical/synthetic counterfactuals, not Seoul observed route payoffs.
"""
from collections import Counter
from dataclasses import dataclass

@dataclass(frozen=True)
class Edge:
    free: float
    linear: float = 0.
    quadratic: float = 0.

    def __post_init__(self):
        if any(x < 0 for x in (self.free,self.linear,self.quadratic)):
            raise ValueError("nonnegative congestion coefficients")

    def latency(self, x):
        if type(x) is not int or x < 0:
            raise ValueError("link flow must be nonnegative integer")
        return self.free+self.linear*x+self.quadratic*x*x

    def system_cost(self,x):
        return x*self.latency(x)


def total_cost(edges,flows):
    return sum(v.system_cost(flows.get(e,0)) for e,v in edges.items())


def route_latency(edges,flows,path):
    return sum(edges[e].latency(flows.get(e,0)) for e in path)


def atomic_reroute_delta(edges,flows,old_path,new_path):
    """Exact social C_after-C_before in O(size of changed path edges).

    Every path is simple, current source car present, static separable links.
    Any road-dependent dynamic spillover invalidates this local certificate.
    """
    if len(set(old_path))!=len(old_path) or len(set(new_path))!=len(new_path):
        raise ValueError("simple paths only")
    gone=set(old_path)-set(new_path)
    gained=set(new_path)-set(old_path)
    if any(e not in edges for e in gone|gained):
        raise ValueError("unknown edge in route")
    delta=0.
    for e in gone:
        q=flows.get(e,0)
        if q<1:
            raise ValueError("old car not present on existing edge")
        delta+=edges[e].system_cost(q-1)-edges[e].system_cost(q)
    for e in gained:
        q=flows.get(e,0)
        delta+=edges[e].system_cost(q+1)-edges[e].system_cost(q)
    return delta


def braess_model():
    edges={"su":Edge(0.,1.),"ut":Edge(45.),"sv":Edge(45.),
           "vt":Edge(0.,1.),"uv":Edge(0.)}
    paths={"upper":("su","ut"),"lower":("sv","vt"),
           "shortcut":("su","uv","vt")}
    return edges,paths


def braess_allocation(counts,edges=None,paths=None):
    if edges is None:
        edges,paths=braess_model()
    flows=Counter()
    for r,n in counts.items():
        if type(n) is not int or n<0:
            raise ValueError("route flow must be nonnegative integer")
        for e in paths[r]:
            flows[e]+=n
    return dict(flows),total_cost(edges,flows)


def braess_exact_optimum(N=40):
    edges,paths=braess_model()
    best=(float("inf"),None)
    for u in range(N+1):
        for l in range(N-u+1):
            counts={"upper":u,"lower":l,"shortcut":N-u-l}
            _,cost=braess_allocation(counts,edges,paths)
            if cost<best[0]:
                best=(cost,counts)
    return dict(N=N,cost=best[0],route_counts=best[1],
                enumerated=(N+1)*(N+2)//2,synthetic_only=True)


def braess_greedy(N=40):
    edges,paths=braess_model()
    counts={"upper":0,"lower":0,"shortcut":N}
    flows,_=braess_allocation(counts,edges,paths)
    moves=0
    while True:
        candidate=None
        for old in paths:
            if not counts[old]:
                continue
            for new in paths:
                if old==new:
                    continue
                d=atomic_reroute_delta(edges,flows,paths[old],paths[new])
                if d < -1e-9 and (candidate is None or d<candidate[0]):
                    candidate=(d,old,new)
        if candidate is None:
            break
        delta,old,new=candidate
        before=total_cost(edges,flows)
        for e in set(paths[old])-set(paths[new]):
            flows[e]-=1
        for e in set(paths[new])-set(paths[old]):
            flows[e]+=1
        counts[old]-=1
        counts[new]+=1
        after=total_cost(edges,flows)
        if abs(after-before-delta)>1e-8:
            raise AssertionError("local exact delta mismatch")
        moves+=1
        if moves>3*N:
            raise AssertionError("unexpected nontermination")
    return dict(N=N,cost=total_cost(edges,flows),route_counts=counts,
                accepted_moves=moves,
                no_general_global_optimality_claim=True)


def homogeneous_affine_dispersion(flows,free=0.,slope=1.):
    """Exact identical STATIC affine-edge micro/macro identity.

    sum_e q_e*(a+b*q_e) = a*Q + b*Q**2/n
                          + b*sum_e(q_e-Q/n)**2 .
    Spatial source sensor passage counts are NOT calibrated vehicle occupancy.
    """
    flows=list(flows)
    if not flows or any(type(x) is not int or x<0 for x in flows):
        raise ValueError("nonempty nonnegative integer link counts")
    if free<0 or slope<0:
        raise ValueError("nonnegative coefficients")
    n=len(flows);Q=sum(flows);mu=Q/n
    base=free*Q+slope*Q*Q/n
    dispersion=slope*sum((q-mu)**2 for q in flows)
    direct=sum(q*(free+slope*q) for q in flows)
    if abs(base+dispersion-direct)>1e-7*max(1,abs(direct)):
        raise AssertionError("exact cost decomposition failure")
    return dict(edges=n,flow_total=Q,homogeneous_reference=base,
                dispersion_surcharge=dispersion,system_cost=direct,
                only_under_identical_affine_static_edges=True)
