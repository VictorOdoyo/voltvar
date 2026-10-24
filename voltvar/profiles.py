from copy import deepcopy
from .model import validate
from .control import local_control,optimize
from .evaluate import state
from .numeric import finite
def scaled(model,load_scale=1,solar_scale=1):
    finite(load_scale,'load scale',0,10);finite(solar_scale,'solar scale',0,10);m=validate(model)
    for load in m['network']['loads']:load['p_mw']*=load_scale;load['q_mvar']*=load_scale
    for inv in m['inverters']:inv['p_mw']*=solar_scale
    return validate(m)
def time_series(model,profile,mode='coordinated',q_levels=3):
    if not 1<=len(profile)<=168 or mode not in ['local','coordinated']:raise ValueError('Invalid profile or mode')
    original=validate(model);previous=state(original);rows=[]
    for i,period in enumerate(profile):
        m=scaled(original,period.get('load_scale',1),period.get('solar_scale',1))
        for d,p in zip(m['taps']+m['capacitors'],previous):d['position']=p
        study=optimize(m,q_levels=q_levels,previous=previous) if mode=='coordinated' else local_control(m,previous=previous)
        result=study['best'] if mode=='coordinated' else study
        rows.append({'period':i,'result':result,'feasible':bool(result and result['feasible'])})
        if result:previous=result['positions']
    return {'periods':rows,'feasible':all(row['feasible'] for row in rows),'switching_operations':sum(row['result']['switching_operations'] for row in rows if row['result']),'assumption':'Sequential myopic control; switching penalty uses previous accepted state.'}
def uncertain_solar(model,scales,**options):
    if not 1<=len(scales)<=50:raise ValueError('Require 1..50 solar scenarios')
    result=optimize(model,**options);best=result['best']
    if best is None:return {'base':result,'robust_feasible':False,'scenarios':[]}
    from .evaluate import assess
    rows=[]
    for scale in scales:
        m=scaled(model,solar_scale=scale)
        # Fixed Q commands must satisfy the capability circle at each solar output.
        try:r=assess(m,best['positions'],best['reactive_mvar']);rows.append({'solar_scale':scale,'feasible':r['feasible'],'result':r})
        except ValueError as exc:rows.append({'solar_scale':scale,'feasible':False,'error':str(exc)})
    return {'base':result,'robust_feasible':all(r['feasible'] for r in rows),'scenarios':rows,'assumption':'Fixed candidate stress test, not a robust optimization certificate.'}
