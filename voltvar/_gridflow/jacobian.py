import numpy as np
from .equations import sets,power

def jacobian(y,v,kinds):
    a,q=sets(kinds);vm=np.abs(v);theta=np.angle(v);s=power(y,v);n=len(v)
    h=np.zeros((n,n));nn=h.copy();m=h.copy();l=h.copy()
    for i in range(n):
        for j in range(n):
            if i==j:
                h[i,i]=-s.imag[i]-y.imag[i,i]*vm[i]**2
                nn[i,i]=s.real[i]/vm[i]+y.real[i,i]*vm[i]
                m[i,i]=s.real[i]-y.real[i,i]*vm[i]**2
                l[i,i]=s.imag[i]/vm[i]-y.imag[i,i]*vm[i]
            else:
                d=theta[i]-theta[j];g,b=y.real[i,j],y.imag[i,j]
                h[i,j]=vm[i]*vm[j]*(g*np.sin(d)-b*np.cos(d))
                nn[i,j]=vm[i]*(g*np.cos(d)+b*np.sin(d))
                m[i,j]=-vm[i]*vm[j]*(g*np.cos(d)+b*np.sin(d))
                l[i,j]=vm[i]*(g*np.sin(d)-b*np.cos(d))
    return np.block([[h[np.ix_(a,a)],nn[np.ix_(a,q)]],[m[np.ix_(q,a)],l[np.ix_(q,q)]]])
