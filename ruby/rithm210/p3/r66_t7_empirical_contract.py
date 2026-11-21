"""Privacy-preserving original-study audit boundaries; synthetic rows only.

This file cannot load raw participant trajectories; it checks SHA and produces
only pooled *treatment x epoch* count summaries from caller-provided events.
No causal adjustment, no per-group or per-session identity, no subject output.
"""
from hashlib import sha256
from pathlib import Path

AUTHORISED_ZIP_SHA256='e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953'
TREATMENTS=('No','Partial','Full','Endogenous')
EPOCHS=('early','late')


def check_authorized_source(path):
    f=Path(path)
    digest=sha256(f.read_bytes()).hexdigest()
    if digest!=AUTHORISED_ZIP_SHA256:
        raise PermissionError('source byte hash not authorized; no raw rows read')
    return True


def pooled_joint_tail(events,cutoff=3):
    """One event per group-period: treatment, epoch, prior_a, a_to_b.

    Returns only pooled counts (not subject IDs or group-level histories).
    `cutoff>=3` is an exploratory tail event; source contains rare events.
    """
    if cutoff<3:
        raise ValueError('cannot redefine the pre-specified 3+ tail')
    out={(c,e):{'opportunities':0,'tail':0} for c in TREATMENTS for e in EPOCHS}
    for ev in events:
        if set(ev)!={'treatment','epoch','prior_a','a_to_b'}:
            raise ValueError('only privacy-minimal fields admitted')
        c,e=ev['treatment'],ev['epoch']
        if (c,e) not in out:
            raise ValueError('invalid treatment/epoch')
        n,k=ev['prior_a'],ev['a_to_b']
        if not isinstance(n,int) or not 0<=n<=6 or not isinstance(k,int) or not 0<=k<=n:
            raise ValueError('invalid occupancy/switches')
        if n==4:
            out[(c,e)]['opportunities']+=1
            out[(c,e)]['tail']+=int(k>=cutoff)
    return {f'{c}_{e}':out[(c,e)] for c in TREATMENTS for e in EPOCHS}
