from copy import deepcopy
from .numeric import finite,integer
from ._gridflow.model import validate as network_validate
from .devices import reactive_capability,tap_ratio,volt_var
def validate(model):
    m=deepcopy(model);m['network']=network_validate(m['network']);n=m['network'];buses={b['id'] for b in n['buses']};branches={b['id'] for b in n['branches']}
    for key in ['taps','capacitors','inverters']:m.setdefault(key,[])
    all_ids=set()
    for kind in ['taps','capacitors','inverters']:
        for device in m[kind]:
            key=device['id']
            if not isinstance(key,str) or not key or key in all_ids:raise ValueError('Unique control IDs required')
            all_ids.add(key)
            if kind=='taps':
                if device['branch'] not in branches:raise ValueError('Unknown tap branch')
                lo=integer(device.get('minimum',-4),'minimum tap',-32,32);hi=integer(device.get('maximum',4),'maximum tap',lo,32)
                integer(device.get('position',0),'position',lo,hi);tap_ratio(lo,device.get('step',.00625));tap_ratio(hi,device.get('step',.00625))
            else:
                if device['bus'] not in buses:raise ValueError('Unknown control bus')
                if next(b for b in n['buses'] if b['id']==device['bus'])['kind']!='PQ':raise ValueError('Reactive devices currently require PQ buses')
                if kind=='capacitors':
                    count=integer(device['maximum'],'maximum steps',0,64);integer(device.get('position',0),'capacitor position',0,count);finite(device['step_mvar'],'capacitor step',0)
                else:
                    cap=reactive_capability(device['p_mw'],device['s_mva'],device.get('q_limit'));finite(device.get('q_mvar',0),'inverter Q',-cap,cap)
                    volt_var(1,device.get('curve',[[.94,1],[.98,0],[1.02,0],[1.06,-1]]),cap)
    m.setdefault('limits',{});limits=m['limits'];lo=finite(limits.get('vmin',.95),'vmin',.1,2);finite(limits.get('vmax',1.05),'vmax',lo,2);finite(limits.get('min_pf',0),'minimum PF',0,1)
    m.setdefault('weights',{})
    for key,value in m['weights'].items():finite(value,'objective weight '+key,0)
    return m
