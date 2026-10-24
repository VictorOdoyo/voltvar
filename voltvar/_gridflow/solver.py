import time
import numpy as np
from .model import validate,injections
from .topology import require_references
from .admittance import ybus
from .equations import power
from .results import report
from . import newton,gauss_seidel,fast_decoupled

def solve(data,method='newton',tolerance=1e-9,max_iterations=None,enforce_q_limits=True):
    if method=='dc':
        from .dc import solve_dc
        return solve_dc(data)
    if method not in ['newton','gauss_seidel','fast_decoupled']:raise ValueError('Unknown solver method')
    if not isinstance(tolerance,(int,float)) or not np.isfinite(tolerance) or not 0<tolerance<1:raise ValueError('Tolerance must be finite and between 0 and 1')
    if max_iterations is not None and (isinstance(max_iterations,bool) or not isinstance(max_iterations,int) or not 0<=max_iterations<=10000):raise ValueError('Invalid iteration limit')
    started=time.perf_counter();n=validate(data);groups=require_references(n);y=ybus(n);s=injections(n)
    kinds=[b['kind'] for b in n['buses']];v=np.array([b['vm']*np.exp(1j*np.deg2rad(b['va_deg'])) for b in n['buses']]);all_history=[];switches=[]
    options={'tolerance':tolerance}
    if max_iterations is not None:options['max_iterations']=max_iterations
    for outer in range(len(kinds)+1):
        if method=='fast_decoupled':v,ok,h,reason=fast_decoupled.solve(n,y,v,s,kinds,**options)
        else:v,ok,h,reason=getattr({'newton':newton,'gauss_seidel':gauss_seidel}[method],'solve')(y,v,s,kinds,**options)
        all_history.append(h)
        if not ok or not enforce_q_limits:break
        calculated=power(y,v);changed=False
        for i,bus in enumerate(n['buses']):
            if kinds[i]!='PV':continue
            gens=[g for g in n['generators'] if g['status'] and g['bus']==bus['id']]
            load=sum(d['q_mvar'] for d in n['loads'] if d['status'] and d['bus']==bus['id'])
            q=calculated.imag[i]*n['base_mva']+load;lo=sum(g['qmin'] for g in gens);hi=sum(g['qmax'] for g in gens)
            bound=lo if q<lo-1e-7 else hi if q>hi+1e-7 else None
            if bound is not None:
                kinds[i]='PQ';s[i]=complex(s.real[i],(bound-load)/n['base_mva']);changed=True
                switches.append({'bus':bus['id'],'required_q_mvar':float(q),'bound_q_mvar':bound,'new_kind':'PQ'})
        if not changed:break
    result=report(n,y,v,kinds,all_history,ok,reason,method,switches);result.update({'islands':groups,'elapsed_seconds':time.perf_counter()-started,'schema_version':1,'assumptions':['Balanced positive-sequence steady-state network. Slack reactive limits are not enforced. PV limits are aggregate per bus and switch irreversibly to PQ during a study.']})
    return result
