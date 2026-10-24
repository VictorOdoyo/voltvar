import numpy as np
from .equations import mismatch,norm,pack,unpack
from .jacobian import jacobian

def solve(y,v,s,kinds,tolerance=1e-9,max_iterations=60):
    v=v.copy();history=[];reason='iteration_limit'
    for iteration in range(max_iterations+1):
        f=mismatch(y,v,s,kinds);error=norm(f);history.append({'iteration':iteration,'mismatch_pu':error})
        if error<=tolerance:return v,True,history,'converged'
        if iteration==max_iterations:break
        try:dx=np.linalg.solve(jacobian(y,v,kinds),f)
        except np.linalg.LinAlgError:return v,False,history,'singular_jacobian'
        x=pack(v,kinds);alpha=1.0;accepted=False
        while alpha>=1/4096:
            candidate=unpack(x+alpha*dx,v,kinds)
            # unpack uses signed magnitudes internally, so guard the actual state as well.
            from .equations import sets
            a,q=sets(kinds)
            if np.all((x+alpha*dx)[len(a):]>.03) and np.all(np.abs(candidate)<3) and norm(mismatch(y,candidate,s,kinds))<error:
                v=candidate;history[-1]['step_scale']=alpha;accepted=True;break
            alpha/=2
        if not accepted:reason='line_search_stalled';break
    return v,False,history,reason
