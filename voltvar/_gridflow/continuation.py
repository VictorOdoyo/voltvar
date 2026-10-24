"""Pseudo-arclength continuation for proportional load scaling, fixed bus types."""
import numpy as np
from .model import validate,injections
from .admittance import ybus
from .solver import solve
from .equations import sets,pack,unpack,power,norm
from .jacobian import jacobian

def continuation(data,steps=30,step_size=.05,tolerance=1e-8):
    if not isinstance(steps,int) or not 1<=steps<=300 or not .001<=step_size<=.3:raise ValueError('Continuation bounds: steps 1..300, step .001.. .3')
    n=validate(data);base=solve(n,enforce_q_limits=False)
    if not base['converged']:raise ValueError('Base point did not converge')
    kinds=[b['kind'] for b in n['buses']];a,q=sets(kinds);y=ybus(n);s0=injections(n);ds=np.zeros(len(kinds),complex);index={b['id']:i for i,b in enumerate(n['buses'])}
    for load in n['loads']:
        if load['status']:ds[index[load['bus']]]-=complex(load['p_mw'],load['q_mvar'])/n['base_mva']
    ds_reduced=np.r_[ds.real[a],ds.imag[q]]
    if norm(ds_reduced)==0:raise ValueError('Continuation requires a nonzero scalable non-slack load')
    reference=np.array([b['vm_pu']*np.exp(1j*np.deg2rad(b['va_deg'])) for b in base['buses']]);state=np.r_[pack(reference,kinds),1.];previous=None;points=[];events=[];reason='step_limit'
    for count in range(steps+1):
        voltage=unpack(state[:-1],reference,kinds);j=jacobian(y,voltage,kinds)
        _,_,vh=np.linalg.svd(np.column_stack([j,-ds_reduced]),full_matrices=True);tangent=vh[-1];tangent/=np.linalg.norm(tangent)
        if (previous is None and tangent[-1]<0) or (previous is not None and np.dot(tangent,previous)<0):tangent=-tangent
        if previous is not None and tangent[-1]*previous[-1]<0:events.append({'type':'load_parameter_turning_point','point':count,'lambda':float(state[-1])})
        expected=s0+(state[-1]-1)*ds;actual=power(y,voltage);residual=np.r_[(actual-expected).real[a],(actual-expected).imag[q]]
        points.append({'lambda':float(state[-1]),'min_voltage_pu':float(np.min(np.abs(voltage))),'vm_pu':np.abs(voltage).tolist(),'va_deg':np.rad2deg(np.angle(voltage)).tolist(),'mismatch_pu':norm(residual),'tangent_lambda':float(tangent[-1])})
        if count==steps:break
        success=False;trial_step=step_size
        while trial_step>=.0005:
            predictor=state+trial_step*tangent;candidate=predictor.copy()
            for iteration in range(15):
                vv=unpack(candidate[:-1],reference,kinds);ss=s0+(candidate[-1]-1)*ds;delta=power(y,vv)-ss
                f=np.r_[delta.real[a],delta.imag[q],np.dot(tangent,candidate-predictor)]
                if norm(f)<tolerance:success=True;break
                aug=np.vstack([np.column_stack([jacobian(y,vv,kinds),-ds_reduced]),tangent])
                try:update=np.linalg.solve(aug,-f)
                except np.linalg.LinAlgError:break
                candidate+=update
                if np.any(candidate[len(a):-1]<.03) or np.any(candidate[len(a):-1]>3) or not np.all(np.isfinite(candidate)):break
            if success:state=candidate;previous=tangent;break
            trial_step/=2
        if not success:reason='corrector_failed';break
    return {'points':points,'events':events,'reason':reason,'bus_ids':[b['id'] for b in n['buses']],'assumptions':['Pseudo-arclength predictor-corrector; loads scale proportionally, generation P stays fixed and slack balances. PV reactive limits and discrete controls are disabled. A sampled turning point is not a certified operating margin.']}
