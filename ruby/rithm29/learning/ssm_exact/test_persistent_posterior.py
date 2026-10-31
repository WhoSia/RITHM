import numpy as np
from persistent_posterior import predict_sequence

p=np.array([[.9]*4+[.1]*5,[.9]*4+[.1]*5,[.9]*4+[.1]*5])
y=np.array([1,1,0])
forecast=predict_sequence(p,y)
assert np.isclose(forecast[0],(4*.9+5*.1)/9)
posterior_after_first=np.array([.9]*4+[.1]*5)/((4*.9+5*.1))
assert np.isclose(forecast[1],posterior_after_first@p[1])
assert np.all((forecast>=0)&(forecast<=1))
assert np.allclose(predict_sequence(p,y)[:2],predict_sequence(p,y[:2])[:2])
assert np.allclose(predict_sequence(np.full((3,9),.7),y),.7)
assert np.allclose(predict_sequence(p,y,lapse=0.5)[0],.5*(4*.9+5*.1)/9+.25)
print("posterior tests pass")
