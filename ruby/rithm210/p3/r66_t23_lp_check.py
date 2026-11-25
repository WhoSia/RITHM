"""Optional independent verifier, not a dependency of the Ruby mainline."""
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

SCRIPT = r'''
rng=Random.new(2302)
puts JSON.generate(Array.new(300){
  k=rng.rand(6);w=Array.new(6){rng.rand(0..9)};w[k]=1 if w.sum==0
  p=w.map{|x|Rational(x,w.sum)};e=Rational(rng.rand(0..10),10)
  l=Rational(rng.rand(1..10),10);route=[:a,:b].sample(random:rng)
  x=RithmT23::Drift.bounds(k,p,route,eps:e,q_min:l)
  {k:k,p:p.map(&:to_f),e:e.to_f,l:l.to_f,route:route,low:x[:low][:gain].to_f,high:x[:high][:gain].to_f}
})
'''
cases = json.loads(subprocess.run(
    ['ruby', '-r', './r66_t23_drift', '-rjson', '-e', SCRIPT],
    cwd=Path(__file__).resolve().parent, check=True, capture_output=True, text=True
).stdout)
error = 0.0
for d in cases:
    k, p, e, l = d['k'], np.array(d['p']), d['e'], d['l']
    r = 1 - p[k]
    off = np.ones(6)
    off[k] = 0
    # Variables: six active masses and t=1/q. No greedy allocator here.
    ub = np.vstack([np.column_stack([np.eye(6), -p]), np.r_[-off, r-e]])
    b = np.r_[np.zeros(6), -e]
    w = (np.arange(6)*3-11)*(1 if d['route'] == 'a' else -1)
    for sign, key in [(1, 'low'), (-1, 'high')]:
        result = linprog(np.r_[sign*w, 0], A_ub=ub, b_ub=b,
                         A_eq=[np.r_[np.ones(6), 0]], b_eq=[1],
                         bounds=[(0, None)]*6+[(1, 1/l)], method='highs')
        assert result.success, (d, result.message)
        delta = abs(sign*result.fun-d[key])
        error = max(error, delta)
        assert delta < 1e-7, (d, result.fun)
print(f'{len(cases)*2} LP objectives, max absolute error {error:.3g}')
