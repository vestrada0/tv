import sys, math, json, numpy as np
sys.path.insert(0,'turn'); sys.path.insert(0,'.')
from sim3 import area, body, kmax, VEH, mouth, ax, rollout, evaluate
from shapely.prepared import prep
from scipy.optimize import minimize
nrm=np.array([-ax[1],ax[0]]); rt=-nrm
C=np.zeros(2); yc=(C-mouth)@ax
def cost(p,v,A,Ap):
    bad,dth,lat,along,tr=evaluate(p,v,A,Ap)
    # also reward clearance
    return bad*50+dth*5+lat*2+max(0,along+2)
def clearance(p,v,A):
    tr=rollout(p,v); m=9
    for q in tr[::2]:
        b=body(q[0],q[1],q[2],v); out=b.difference(A).area
        c=-out if out>1e-6 else A.boundary.distance(b); m=min(m,c)
    return m,tr
res={}
for vn in ('car','pickup','van'):
    v=VEH[vn]; km=kmax(v)
    for full in (False,True):
        A=area(full); Ap=prep(A); best=None
        for r in (5.2,5.6,6.0):
            for re in (4.6,5.0,5.4,5.8):
                for tl in (0.5,1.5,2.5):
                    p0=[5+v[0]+yc-tl,0,0,-1/(r*km),1.5*math.pi*r,1/(re*km),0.5*math.pi*re,6]
                    r_=minimize(cost,p0,args=(v,A,Ap),method='Nelder-Mead',options=dict(maxiter=600,xatol=1e-3,fatol=1e-4))
                    p=r_.x.copy(); p[1]=0; p[2]=0
                    p[3]=max(-1,min(1,p[3])); p[5]=max(-1,min(1,p[5]))
                    bad,dth,lat,along,_=evaluate(p,v,A,Ap)
                    if dth>0.15 or lat>0.6: continue
                    c,_=clearance(p,v,A)
                    if best is None or c>best[0]: best=(c,list(map(float,p)),math.degrees(dth),lat)
        key=f'{vn}_{"full" if full else "own"}'
        res[key]=best
        if best: print(f'{vn:7s} {"full circle" if full else "own land  "}: clearance {best[0]*100:+.0f} cm  (heading err {best[2]:.0f}°, lateral {best[3]:.2f} m)',flush=True)
        else: print(f'{vn:7s} {"full circle" if full else "own land  "}: no collision-free path that returns to the passage',flush=True)
json.dump(res,open('turn/refine.json','w'))
