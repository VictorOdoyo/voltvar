import numpy as np
from .equations import mismatch,norm,power

def solve(y,v,s,kinds,tolerance=1e-9,max_iterations=3000):
    v=v.copy();fixed=np.abs(v).copy();history=[]
    for iteration in range(max_iterations+1):
        error=norm(mismatch(y,v,s,kinds));history.append({'iteration':iteration,'mismatch_pu':error})
        if error<=tolerance:return v,True,history,'converged'
        if iteration==max_iterations:break
        for i,kind in enumerate(kinds):
            if kind=='Slack':continue
            if abs(y[i,i])<1e-14 or abs(v[i])<.03:return v,False,history,'singular_update'
            q=power(y,v).imag[i] if kind=='PV' else s.imag[i]
            updated=(complex(s.real[i],-q)/v[i].conjugate()-(y[i]@v-y[i,i]*v[i]))/y[i,i]
            if kind=='PV':
                if abs(updated)==0:return v,False,history,'zero_pv_voltage'
                updated=fixed[i]*updated/abs(updated)
            v[i]=updated
        if not np.all(np.isfinite(v)) or np.max(np.abs(v))>3:return v,False,history,'diverged'
    return v,False,history,'iteration_limit'
