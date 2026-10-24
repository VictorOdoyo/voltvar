import numpy as np
from .model import validate,injections
from .topology import require_references

def solve_dc(data):
    n=validate(data);groups=require_references(n);index={b['id']:i for i,b in enumerate(n['buses'])};size=len(index)
    bmat=np.zeros((size,size));shift=np.zeros(size);theta=np.deg2rad([b['va_deg'] for b in n['buses']]);p=injections(n).real
    p-=np.array([b['gs_mw'] for b in n['buses']])/n['base_mva']
    for branch in n['branches']:
        if not branch['status']:continue
        if branch['x']==0:raise ValueError('DC model requires nonzero reactance')
        i,j=index[branch['from']],index[branch['to']];b=1/(branch['x']*branch['tap']);phi=np.deg2rad(branch['shift_deg'])
        bmat[i,i]+=b;bmat[j,j]+=b;bmat[i,j]-=b;bmat[j,i]-=b;shift[i]-=b*phi;shift[j]+=b*phi
    free=[i for i,b in enumerate(n['buses']) if b['kind']!='Slack'];ref=[i for i in range(size) if i not in free]
    try:theta[free]=np.linalg.solve(bmat[np.ix_(free,free)],p[free]-shift[free]-bmat[np.ix_(free,ref)]@theta[ref])
    except np.linalg.LinAlgError as exc:raise ValueError('Singular DC network') from exc
    flows=[]
    for branch in n['branches']:
        flow=0.
        if branch['status']:flow=(theta[index[branch['from']]]-theta[index[branch['to']]]-np.deg2rad(branch['shift_deg']))/(branch['x']*branch['tap'])*n['base_mva']
        flows.append({'id':branch['id'],'p_from_mw':float(flow),'p_to_mw':float(-flow),'loading_percent':abs(float(flow))/branch['rate_mva']*100 if branch['rate_mva'] else None})
    return {'method':'dc','converged':True,'islands':groups,'buses':[{'id':b['id'],'vm_pu':1.,'va_deg':float(np.rad2deg(theta[i])),'p_injection_mw':float((bmat@theta+shift)[i]*n['base_mva'])} for i,b in enumerate(n['buses'])],'branches':flows,'losses_mw':0.,'assumptions':['Lossless small-angle model with unit voltage magnitudes; loading uses MW against an MVA rating and is approximate.']}
