import numpy as np
from .solver import solve
from .model import validate
from .admittance import ybus
from .jacobian import jacobian
from .equations import sets

def sensitivity(data):
    n=validate(data);base=solve(n)
    if not base['converged']:raise ValueError('Sensitivity requires a converged operating point')
    v=np.array([b['vm_pu']*np.exp(1j*np.deg2rad(b['va_deg'])) for b in base['buses']]);kinds=[b['kind'] for b in base['buses']];a,q=sets(kinds);j=jacobian(ybus(n),v,kinds)
    try:inverse=np.linalg.inv(j)/n['base_mva']
    except np.linalg.LinAlgError as exc:raise ValueError('Singular sensitivity Jacobian') from exc
    return {'operating_point':base,'condition_number':float(np.linalg.cond(j)) if j.size else 1.,'state_labels':['angle_rad:'+n['buses'][i]['id'] for i in a]+['vm_pu:'+n['buses'][i]['id'] for i in q],'injection_labels':['P_MW:'+n['buses'][i]['id'] for i in a]+['Q_MVAr:'+n['buses'][i]['id'] for i in q],'derivatives':inverse.tolist(),'assumptions':['Local fixed-active-set derivative for positive injection; increasing demand has the opposite sign. Tap positions and PV/PQ types remain fixed.']}
