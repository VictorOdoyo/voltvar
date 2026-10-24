import numpy as np

def primitive(branch):
    y=1/complex(branch['r'],branch['x']);charging=1j*branch['b']/2
    t=branch['tap']*np.exp(1j*np.deg2rad(branch['shift_deg']))
    return (y+charging)/(abs(t)**2),-y/t.conjugate(),-y/t,y+charging

def ybus(n):
    index={b['id']:i for i,b in enumerate(n['buses'])};y=np.zeros((len(index),len(index)),complex)
    for branch in n['branches']:
        if not branch['status']:continue
        i,j=index[branch['from']],index[branch['to']];ff,ft,tf,tt=primitive(branch)
        y[i,i]+=ff;y[i,j]+=ft;y[j,i]+=tf;y[j,j]+=tt
    for i,b in enumerate(n['buses']):y[i,i]+=complex(b['gs_mw'],b['bs_mvar'])/n['base_mva']
    return y
