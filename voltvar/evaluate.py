from copy import deepcopy
import math
from .model import validate
from .devices import tap_ratio,reactive_capability,power_factor,switching_operations
from ._gridflow.solver import solve
def state(model):return [d.get('position',0) for d in model['taps']+model['capacitors']]
def apply(model,positions=None,reactive=None):
    m=validate(model);n=deepcopy(m['network']);positions=state(m) if positions is None else list(positions)
    if len(positions)!=len(m['taps'])+len(m['capacitors']):raise ValueError('Wrong decision count')
    offset=0
    for d in m['taps']:
        p=positions[offset];offset+=1
        if isinstance(p,bool) or not isinstance(p,int) or not d.get('minimum',-4)<=p<=d.get('maximum',4):raise ValueError('Tap position outside bounds')
        next(b for b in n['branches'] if b['id']==d['branch'])['tap']=tap_ratio(p,d.get('step',.00625))
    for d in m['capacitors']:
        p=positions[offset];offset+=1
        if isinstance(p,bool) or not isinstance(p,int) or not 0<=p<=d['maximum']:raise ValueError('Capacitor position outside bounds')
        next(b for b in n['buses'] if b['id']==d['bus'])['bs_mvar']+=p*d['step_mvar']
    reactive=reactive or {}
    for d in m['inverters']:
        cap=reactive_capability(d['p_mw'],d['s_mva'],d.get('q_limit'));q=reactive.get(d['id'],d.get('q_mvar',0))
        if not math.isfinite(q) or abs(q)>cap+1e-9:raise ValueError('Inverter Q outside capability')
        n['generators'].append({'id':'control:'+d['id'],'bus':d['bus'],'p_mw':d['p_mw'],'q_mvar':q})
    return m,n,positions
def assess(model,positions=None,reactive=None,previous=None):
    m,n,positions=apply(model,positions,reactive);r=solve(n);limits=m['limits'];vmin=limits.get('vmin',.95);vmax=limits.get('vmax',1.05)
    voltages=[b['vm_pu'] for b in r['buses']];violation=sum(max(vmin-x,0)**2+max(x-vmax,0)**2 for x in voltages)
    loading=max((b['loading_percent'] or 0 for b in r['branches']),default=0);overload=sum(max((b['loading_percent'] or 0)/100-1,0)**2 for b in r['branches'])
    slack=[b for b in r['buses'] if b['kind']=='Slack'];p=sum(b['required_generation_mw'] for b in slack);q=sum(b['required_generation_mvar'] for b in slack);pf=power_factor(p,q)
    deviation=sum((x-1)**2 for x in voltages);ops=switching_operations(state(m) if previous is None else previous,positions);w=m['weights']
    score=w.get('loss',1)*r['losses_mw']+w.get('voltage',10)*deviation+w.get('switching',.001)*ops
    feasible=r['converged'] and violation<=1e-14 and overload<=1e-14 and pf+1e-9>=limits.get('min_pf',0)
    return {'converged':r['converged'],'feasible':feasible,'score':score,'losses_mw':r['losses_mw'],'min_voltage_pu':min(voltages),'max_voltage_pu':max(voltages),'max_loading_percent':loading,'power_factor':pf,'voltage_violation_squared':violation,'overload_squared':overload,'switching_operations':ops,'positions':positions,'reactive_mvar':reactive or {d['id']:d.get('q_mvar',0) for d in m['inverters']},'power_flow':r}
