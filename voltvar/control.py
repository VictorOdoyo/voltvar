import itertools,math
from copy import deepcopy
from .model import validate
from .devices import reactive_capability,volt_var
from .evaluate import assess,state
from .numeric import integer,finite
def local_control(model,positions=None,max_iterations=60,tolerance=1e-6,damping=.4,previous=None):
    m=validate(model);integer(max_iterations,'iterations',1,200);finite(tolerance,'tolerance',1e-10,.1);finite(damping,'damping',.001,1)
    q={d['id']:d.get('q_mvar',0) for d in m['inverters']};history=[]
    for iteration in range(max_iterations):
        result=assess(m,positions,q,previous);voltage={b['id']:b['vm_pu'] for b in result['power_flow']['buses']}
        if not result['converged']:return dict(result,control_converged=False,control_history=history)
        target={d['id']:volt_var(voltage[d['bus']],d.get('curve',[[.94,1],[.98,0],[1.02,0],[1.06,-1]]),reactive_capability(d['p_mw'],d['s_mva'],d.get('q_limit'))) for d in m['inverters']}
        error=max((abs(target[key]-q[key]) for key in q),default=0);history.append({'iteration':iteration,'maximum_q_error_mvar':error,'min_voltage_pu':result['min_voltage_pu']})
        if error<tolerance:return dict(result,control_converged=True,control_history=history)
        q={key:q[key]+damping*(target[key]-q[key]) for key in q}
    return dict(assess(m,positions,q,previous),control_converged=False,feasible=False,control_history=history)
def optimize(model,max_candidates=2000,q_levels=3,previous=None):
    m=validate(model);integer(max_candidates,'candidate limit',1,20000);integer(q_levels,'Q levels',1,9)
    ranges=[list(range(d.get('minimum',-4),d.get('maximum',4)+1)) for d in m['taps']]+[list(range(d['maximum']+1)) for d in m['capacitors']]
    q_ranges=[]
    for d in m['inverters']:
        cap=reactive_capability(d['p_mw'],d['s_mva'],d.get('q_limit'));q_ranges.append([0.] if q_levels==1 else [-cap+2*cap*j/(q_levels-1) for j in range(q_levels)])
    count=math.prod(map(len,ranges+q_ranges))
    if count>max_candidates:raise ValueError(f'Discrete search needs {count} candidates; narrow ranges or raise limit')
    best=None;screen=[]
    for values in itertools.product(*(ranges+q_ranges)):
        pos=list(values[:len(ranges)]);q={d['id']:values[len(ranges)+i] for i,d in enumerate(m['inverters'])}
        try:r=assess(m,pos,q,previous)
        except (ValueError,ArithmeticError):continue
        screen.append({k:r[k] for k in ['positions','reactive_mvar','feasible','score','min_voltage_pu','max_voltage_pu','switching_operations']})
        if r['feasible'] and (best is None or r['score']<best['score']):best=r
    return {'best':best,'feasible':best is not None,'evaluated':len(screen),'requested':count,'candidates':screen,'assumptions':['Global optimum only over enumerated discrete Q/tap/capacitor grid.','AC balanced positive-sequence checks at every candidate.','No claim of continuous nonlinear OPF optimality.']}
