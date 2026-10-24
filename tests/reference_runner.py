import numpy as np
from copy import deepcopy
from voltvar.devices import *
from voltvar.evaluate import assess,apply
from voltvar.control import optimize,local_control
from voltvar.profiles import scaled,time_series
CURVE=[[.94,1],[.98,0],[1.02,0],[1.06,-1]]
def model(network):return {'network':deepcopy(network),'taps':[],'capacitors':[],'inverters':[],'limits':{'vmin':.8,'vmax':1.2}}
def verify(test,c):
    f=c['family'];a=c['inputs'];e=c['expected']
    if f=='capability':actual=reactive_capability(a['p'],a['s'])
    elif f=='q_limit':actual=reactive_capability(a['p'],a['s'],a['limit'])
    elif f in ['curve_interpolation','curve_clamp']:actual=volt_var(a['voltage'],CURVE,a['capability'])
    elif f=='tap_ratio':actual=tap_ratio(a['position'],a['step'])
    elif f=='capacitor_output':actual=capacitor_output(a['steps'],a['step'],a['voltage'])
    elif f=='power_factor':actual=power_factor(a['p'],a['q'])
    elif f=='switch_count':actual=switching_operations(a['previous'],a['current'])
    else:
        m=model(a['network'])
        if f=='apply_tap':
            m['taps']=[{'id':'t','branch':'l','minimum':-10,'maximum':10,'position':0}];_,n,_=apply(m,[a['position']]);actual=n['branches'][0]['tap'];test.assertNotIn('tap',a['network']['branches'][0])
        elif f in ['apply_shunt','capacitive_voltage']:
            m['capacitors']=[{'id':'c','bus':'d','maximum':10,'position':a['steps'],'step_mvar':a['step']}]
            if f=='apply_shunt':actual=apply(m)[1]['buses'][1]['bs_mvar']
            else:actual=next(b['vm_pu'] for b in assess(m)['power_flow']['buses'] if b['id']=='d')
        elif f=='inverter_injection':
            m['inverters']=[{'id':'i','bus':'d','p_mw':a['p'],'s_mva':2,'q_mvar':a['q']}];n=apply(m)[1];actual=[n['generators'][-1]['p_mw'],n['generators'][-1]['q_mvar']]
        elif f=='resistive_voltage':actual=assess(m)['power_flow']['buses'][1]['vm_pu']
        elif f=='optimum_neutral_tap':
            m['taps']=[{'id':'t','branch':'l','minimum':-a['span'],'maximum':a['span']}];r=optimize(m);test.assertTrue(r['feasible']);actual=r['best']['positions']
        elif f=='infeasible_limits':m['limits']={'vmin':a['vmin'],'vmax':1.2};actual=optimize(m)['feasible']
        elif f=='local_deadband':
            m['inverters']=[{'id':'i','bus':'d','p_mw':a['p'],'s_mva':1,'curve':CURVE}];r=local_control(m);test.assertTrue(r['control_converged']);actual=r['reactive_mvar']['i']
        elif f=='profile_load':
            r=scaled(m,a['load_scale']);actual=[r['network']['loads'][0][k] for k in ['p_mw','q_mvar']]
        elif f=='solar_scale':m['inverters']=[{'id':'i','bus':'d','p_mw':.2,'s_mva':2}];actual=scaled(m,solar_scale=a['solar_scale'])['inverters'][0]['p_mw']
        elif f=='switch_penalty':
            m['taps']=[{'id':'t','branch':'l','minimum':-10,'maximum':10}];m['weights']={'switching':a['weight']};actual=assess(m,[0],previous=a['previous'])['score']
        else:
            m['taps']=[{'id':'t','branch':'l','minimum':-1,'maximum':1}];r=time_series(m,[{}]*a['periods']);actual=[len(r['periods']),r['switching_operations']];test.assertTrue(r['feasible'])
    np.testing.assert_allclose(actual,e,rtol=1e-7,atol=1e-7)
