import numpy as np

def sets(kinds):
    return np.array([i for i,k in enumerate(kinds) if k!='Slack'],int),np.array([i for i,k in enumerate(kinds) if k=='PQ'],int)
def power(y,v):return v*np.conj(y@v)
def mismatch(y,v,s,kinds):
    a,q=sets(kinds);d=s-power(y,v)
    return np.r_[d.real[a],d.imag[q]]
def norm(vector):return float(np.max(np.abs(vector))) if len(vector) else 0.0
def pack(v,kinds):
    a,q=sets(kinds);return np.r_[np.angle(v)[a],np.abs(v)[q]]
def unpack(x,vref,kinds):
    a,q=sets(kinds);angles=np.angle(vref).copy();vm=np.abs(vref).copy()
    angles[a]=x[:len(a)];vm[q]=x[len(a):]
    return vm*np.exp(1j*angles)
