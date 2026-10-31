"""Exhaustive proof witness for six-player two-route switching identity."""
from itertools import product
for before in product((0,1), repeat=6):
    for after in product((0,1), repeat=6):
        u=sum(x==0 and y==1 for x,y in zip(before,after))
        d=sum(x==1 and y==0 for x,y in zip(before,after))
        s=sum(x!=y for x,y in zip(before,after))
        net=sum(after)-sum(before)
        assert s==u+d
        assert net==u-d
        assert s-abs(net)==2*min(u,d)
print("4096 joint before/after combinations verified")
