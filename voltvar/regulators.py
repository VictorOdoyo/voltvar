"""Bounded local discrete regulator logic; no silent oscillation acceptance."""
from .model import validate
from .evaluate import state
from .control import local_control
from .numeric import integer,finite
def regulate(model,max_rounds=40,target_pu=1,deadband_pu=.01,previous=None):
    m=validate(model);integer(max_rounds,'control rounds',1,200);finite(target_pu,'target',.5,1.5);finite(deadband_pu,'deadband',.0001,.2)
    positions=state(m);initial=positions[:] if previous is None else previous;history=[];seen=set()
    branches={b['id']:b for b in m['network']['branches']}
    for iteration in range(max_rounds):
        signature=tuple(positions)
        if signature in seen:
            result=local_control(m,positions,previous=initial)
            return dict(result,feasible=False,discrete_converged=False,discrete_reason='control_cycle',discrete_history=history)
        seen.add(signature);result=local_control(m,positions,previous=initial)
        if not result['control_converged']:return dict(result,feasible=False,discrete_converged=False,discrete_reason='inverter_not_converged',discrete_history=history)
        voltage={b['id']:b['vm_pu'] for b in result['power_flow']['buses']};updated=positions[:];offset=0
        for tap in m['taps']:
            bus=tap.get('controlled_bus',branches[tap['branch']]['to'])
            if bus not in voltage:raise ValueError('Unknown regulator controlled bus')
            value=voltage[bus];change=-1 if value<target_pu-deadband_pu else 1 if value>target_pu+deadband_pu else 0
            updated[offset]=max(tap.get('minimum',-4),min(tap.get('maximum',4),positions[offset]+change));offset+=1
        for bank in m['capacitors']:
            value=voltage[bank['bus']];change=1 if value<target_pu-deadband_pu else -1 if value>target_pu+deadband_pu else 0
            updated[offset]=max(0,min(bank['maximum'],positions[offset]+change));offset+=1
        history.append({'round':iteration,'positions':positions[:],'next_positions':updated[:]})
        if updated==positions:return dict(result,discrete_converged=True,discrete_reason='settled_or_at_bounds',discrete_history=history)
        positions=updated
    return dict(local_control(m,positions,previous=initial),feasible=False,discrete_converged=False,discrete_reason='round_limit',discrete_history=history)
