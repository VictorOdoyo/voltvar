from copy import deepcopy
import numpy as np
from .admittance import ybus
from .equations import sets,mismatch,norm

def matrices(network,kinds):
    prime=deepcopy(network);double=deepcopy(network)
    for b in prime['buses']:b['gs_mw']=0;b['bs_mvar']=0
    for b in prime['branches']:b['r']=0;b['b']=0;b['tap']=1
    for b in double['branches']:b['shift_deg']=0
    if any(b['status'] and b['x']==0 for b in prime['branches']):raise ValueError('FDXB requires nonzero branch reactances')
    a,q=sets(kinds)
    return -ybus(prime).imag[np.ix_(a,a)],-ybus(double).imag[np.ix_(q,q)]

def solve(network,y,v,s,kinds,tolerance=1e-9,max_iterations=300):
    a,q=sets(kinds);bp,bq=matrices(network,kinds);v=v.copy();history=[]
    for iteration in range(max_iterations+1):
        error=norm(mismatch(y,v,s,kinds));history.append({'iteration':iteration,'mismatch_pu':error})
        if error<=tolerance:return v,True,history,'converged'
        if iteration==max_iterations:break
        try:
            d=mismatch(y,v,s,kinds);angle=np.angle(v);vm=np.abs(v)
            angle[a]+=np.linalg.solve(bp,d[:len(a)]/vm[a]);v=vm*np.exp(1j*angle)
            d=mismatch(y,v,s,kinds)
            if len(q):vm[q]+=np.linalg.solve(bq,d[len(a):]/vm[q])
            if np.any(vm<.03) or np.any(vm>3):return v,False,history,'diverged'
            v=vm*np.exp(1j*angle)
        except np.linalg.LinAlgError:return v,False,history,'singular_decoupled_matrix'
    return v,False,history,'iteration_limit'
