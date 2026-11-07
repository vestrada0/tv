import sys, math, json, numpy as np
from bulb import *
def balloon(v,sc,r,ra,step=0.15):
    O=np.array([sc,NC]); d=math.sqrt(r*r+2*r*ra); s1=sc-d
    alpha=math.pi/2-math.atan2(ra,d)
    pts=[]
    for s in np.arange(m_in[0]-12,s1,step): pts.append((s,NC,0.0))
    Ca=np.array([s1,NC-ra])                       # right turn (clockwise)
    for a in np.arange(0,alpha,step/ra):
        p=Ca+ra*np.array([math.sin(a),math.cos(a)]); pts.append((p[0],p[1],-a))
    # tangent point -> loop CCW around O
    tp=Ca+ra*(O-Ca)/np.linalg.norm(O-Ca); a0=math.atan2(tp[1]-O[1],tp[0]-O[0])
    beta=math.pi+2*alpha
    for b in np.arange(0,beta,step/r):
        ang=a0+b; p=O+r*np.array([math.cos(ang),math.sin(ang)]); pts.append((p[0],p[1],ang+math.pi/2))
    # mirror exit: right turn around Cb=(s1, NC+ra)
    Cb=np.array([s1,NC+ra]); tp2=Cb+ra*(O-Cb)/np.linalg.norm(O-Cb)
    a1=math.atan2(tp2[1]-Cb[1],tp2[0]-Cb[0])
    for c in np.arange(0,alpha,step/ra):
        ang=a1-c; p=Cb+ra*np.array([math.cos(ang),math.sin(ang)]); pts.append((p[0],p[1],ang-math.pi/2))
    for s in np.arange(s1,m_in[0]-12,-step): pts.append((s,NC,math.pi))
    return pts
def clearance(v,pts,A):
    m=9; worst=None
    for (x,y,th) in pts[::2]:
        b=body(x,y,th,v); out=b.difference(A).area
        c=-out if out>1e-6 else A.boundary.distance(b)
        if c<m: m=c; worst=(x,y,th)
    return m,worst
if __name__=='__main__':
    Rb=float(sys.argv[1]); e=float(sys.argv[2]); sc=Rb+e; A=drivable(Rb,sc)
    res={}
    for vn in ('car','pickup','van','truck'):
        v=VEH[vn]; rmin=1/kmax(v); best=None
        for r in np.arange(rmin,rmin+2.6,0.2):
            for ra in np.arange(rmin,rmin+6.1,0.5):
                pts=balloon(v,sc,r,ra); c,w=clearance(v,pts,A)
                if best is None or c>best[0]: best=(c,r,ra,w)
        res[vn]=dict(clr=best[0],r=best[1],ra=best[2])
        print(f'Ø{2*Rb:.1f} neck+{e}: {vn:6s} best clearance {best[0]*100:+.0f} cm (loop r={best[1]:.1f} m, swing r={best[2]:.1f} m)',flush=True)
    json.dump(res,open(f'quick_{Rb}_{e}.json','w'))
