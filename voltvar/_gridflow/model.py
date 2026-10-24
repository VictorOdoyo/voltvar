"""Schema v1: MW, MVAr, kV, degrees; branch impedances on system MVA base."""
from copy import deepcopy
import math

def number(value,name,minimum=None,positive=False):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError(name+' must be finite numeric data')
    if minimum is not None and (value<minimum or (positive and value==minimum)):
        raise ValueError(name+' is outside its permitted range')
    return float(value)

def validate(data):
    if not isinstance(data,dict): raise ValueError('Network must be an object')
    n=deepcopy(data);n.setdefault('schema_version',1)
    if n['schema_version']!=1: raise ValueError('Unsupported schema version')
    n['base_mva']=number(n.get('base_mva',100),'base_mva',0,True)
    for key in ['buses','branches','loads','generators']: n.setdefault(key,[])
    if not 1<=len(n['buses'])<=500: raise ValueError('Require 1 to 500 buses')
    if len(n['branches'])>2000: raise ValueError('At most 2000 branches are supported')
    ids=set()
    for b in n['buses']:
        if not isinstance(b.get('id'),str) or not b['id'] or b['id'] in ids: raise ValueError('Bus IDs must be unique nonempty strings')
        ids.add(b['id']);b.setdefault('kind','PQ')
        if b['kind'] not in ['Slack','PV','PQ']: raise ValueError('Bus kind must be Slack, PV or PQ')
        for key,default in [('vm',1),('va_deg',0),('base_kv',110),('gs_mw',0),('bs_mvar',0)]:b[key]=number(b.get(key,default),key)
        if b['vm']<=0 or b['base_kv']<=0:raise ValueError('Voltage magnitudes and bases must be positive')
    for kind in ['branches','loads','generators']:
        used=set()
        for item in n[kind]:
            if not isinstance(item.get('id'),str) or not item['id'] or item['id'] in used:raise ValueError(kind+' IDs must be unique')
            used.add(item['id']);item.setdefault('status',True)
            if not isinstance(item['status'],bool):raise ValueError('Status must be boolean')
            keys=['from','to'] if kind=='branches' else ['bus']
            if any(item.get(key) not in ids for key in keys):raise ValueError('Equipment references an unknown bus')
            if kind=='branches':
                if item['from']==item['to']:raise ValueError('Self loops are unsupported')
                for key,default in [('r',0),('x',.1),('b',0),('tap',1),('shift_deg',0),('rate_mva',0)]:item[key]=number(item.get(key,default),key)
                if item['r']<0 or item['rate_mva']<0 or item['tap']<=0 or complex(item['r'],item['x'])==0:raise ValueError('Invalid branch impedance, tap or rating')
            else:
                for key in ['p_mw','q_mvar']:item[key]=number(item.get(key,0),key)
                if kind=='generators':
                    item['qmin']=number(item.get('qmin',-1e6),'qmin');item['qmax']=number(item.get('qmax',1e6),'qmax')
                    if item['qmin']>item['qmax']:raise ValueError('Generator reactive bounds are reversed')
    for b in n['buses']:
        if b['kind'] in ['Slack','PV'] and not any(x['bus']==b['id'] and x['status'] for x in n['generators']):raise ValueError('Controlled buses require an online generator')
    return n

def injections(n):
    import numpy as np
    index={b['id']:i for i,b in enumerate(n['buses'])};s=np.zeros(len(index),complex)
    for sign,kind in [(1,'generators'),(-1,'loads')]:
        for item in n[kind]:
            if item['status']:s[index[item['bus']]]+=sign*complex(item['p_mw'],item['q_mvar'])/n['base_mva']
    return s
