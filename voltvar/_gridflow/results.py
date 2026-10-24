import numpy as np
from .admittance import primitive
from .equations import power

def report(n,y,v,kinds,history,converged,reason,method,switches):
    index={b['id']:i for i,b in enumerate(n['buses'])};injection=power(y,v)*n['base_mva'];flows=[];loss=0j
    for b in n['branches']:
        sf=st=0j
        if b['status']:
            i,j=index[b['from']],index[b['to']];ff,ft,tf,tt=primitive(b)
            sf=v[i]*np.conj(ff*v[i]+ft*v[j])*n['base_mva'];st=v[j]*np.conj(tf*v[i]+tt*v[j])*n['base_mva']
        loss+=sf+st
        flows.append({'id':b['id'],'p_from_mw':float(sf.real),'q_from_mvar':float(sf.imag),'p_to_mw':float(st.real),'q_to_mvar':float(st.imag),'loss_mw':float((sf+st).real),'loading_percent':float(max(abs(sf),abs(st)))/b['rate_mva']*100 if b['rate_mva'] else None})
    buses=[]
    for i,b in enumerate(n['buses']):
        load=sum(complex(d['p_mw'],d['q_mvar']) for d in n['loads'] if d['status'] and d['bus']==b['id'])
        generation=injection[i]+load
        buses.append({'id':b['id'],'kind':kinds[i],'vm_pu':float(abs(v[i])),'va_deg':float(np.rad2deg(np.angle(v[i]))),'p_injection_mw':float(injection[i].real),'q_injection_mvar':float(injection[i].imag),'required_generation_mw':float(generation.real),'required_generation_mvar':float(generation.imag)})
    return {'method':method,'converged':converged,'reason':reason,'iterations':sum(len(h)-1 for h in history),'history':history,'buses':buses,'branches':flows,'losses_mw':float(loss.real),'branch_net_var_mvar':float(loss.imag),'reactive_switches':switches,'shunt_loss_mw':float(sum(b['gs_mw']*abs(v[i])**2 for i,b in enumerate(n['buses']))),'max_mismatch_pu':history[-1][-1]['mismatch_pu'] if history else 0}
