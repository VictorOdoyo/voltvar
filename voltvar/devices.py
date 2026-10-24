import math
import numpy as np
from .numeric import finite,integer
def reactive_capability(p_mw,s_mva,q_limit=None):
    finite(p_mw,'active power');finite(s_mva,'apparent rating',0)
    if abs(p_mw)>s_mva+1e-12:raise ValueError('Active power exceeds inverter rating')
    limit=math.sqrt(max(0,s_mva*s_mva-p_mw*p_mw))
    return min(limit,finite(q_limit,'reactive rating',0)) if q_limit is not None else limit
def volt_var(voltage,curve,capability):
    finite(voltage,'voltage',.01,3);finite(capability,'capability',0)
    if len(curve)<2:raise ValueError('At least two control points required')
    for point in curve:
        finite(point[0],'curve voltage',.01,3);finite(point[1],'curve q fraction',-1,1)
    if any(b[0]<=a[0] for a,b in zip(curve,curve[1:])):raise ValueError('Curve voltages must increase')
    return float(np.interp(voltage,[r[0] for r in curve],[r[1] for r in curve]))*capability
def tap_ratio(position,step=.00625,neutral=1):
    integer(position,'tap',-32,32);finite(step,'tap step',.0001,.1);finite(neutral,'neutral ratio',.1,3)
    ratio=neutral+position*step
    if ratio<=0:raise ValueError('Nonpositive tap ratio')
    return ratio
def capacitor_output(steps,step_mvar,voltage=1):
    integer(steps,'capacitor steps',0,64);finite(step_mvar,'step MVAr',0);finite(voltage,'voltage',.01,3)
    return steps*step_mvar*voltage*voltage
def power_factor(p,q):
    finite(p,'P');finite(q,'Q');s=math.hypot(p,q)
    return abs(p)/s if s else 1.
def switching_operations(previous,current):
    if len(previous)!=len(current):raise ValueError('Control state lengths differ')
    return sum(abs(int(a)-int(b)) for a,b in zip(previous,current))
