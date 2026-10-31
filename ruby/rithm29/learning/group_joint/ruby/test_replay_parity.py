"""Compare Ruby real-data replay against prior independent Python predictions."""
import pandas as pd
import numpy as np
import sys
ruby, python = map(pd.read_csv,sys.argv[1:3])
k=["trt","session","section","Group","Period"]
a=ruby.merge(python,on=k,validate="one_to_one",suffixes=("_ruby","_python"))
assert len(a)==5616
for c in ("U","D","S","absnet","cancel","p_ud","p_cancel","e_switch","e_absnet"):
    gap=np.abs(a[c+"_ruby"]-a[c+"_python"]).max()
    assert gap < 1e-10,(c,gap)
print("5616 rows matched; integer outcomes exact, probabilities <1e-10")
