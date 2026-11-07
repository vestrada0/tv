import sys, math, json, numpy as np
sys.path.insert(0,'.')
from geo import P, C, R, Rin, parcel
from shapely.geometry import Polygon, Point, LineString
from shapely.prepared import prep
from shapely import affinity
from scipy.optimize import differential_evolution
k=0.07032598126928438
T=lambda g: affinity.affine_transform(g,[k,0,0,-k,-C[0]*k,C[1]*k])
tm=lambda p: np.array([(p[0]-C[0])*k,-(p[1]-C[1])*k])
par=T(parcel)
corr=T(Polygon([P[13],P[14],P[16],P[18],P[19],P[20]]))
ring_full=Point(0,0).buffer(R*k,256)
island=Point(0,0).buffer(Rin*k,256)
def area(paved_full):
    ring=ring_full if paved_full else ring_full.intersection(par)
    return ring.union(corr).buffer(0.01).difference(island)
# corridor axis
m13,m20=tm(P[13]),tm(P[20]); m18,m19=tm(P[18]),tm(P[19])
mouth=(m13+m20)/2; street=(m18+m19)/2
ax=(mouth-street)/np.linalg.norm(mouth-street)   # direction into parcel
VEH={'car':(2.70,1.80,0.90,1.00,1.55,5.5),'pickup':(3.30,1.95,0.95,1.30,1.65,6.3),'van':(3.67,2.02,1.00,1.20,1.73,6.5)}
def body(x,y,th,v):
    wb,w,fo,ro,tr,rm=v
    pts=np.array([[-ro,-w/2],[wb+fo,-w/2],[wb+fo,w/2],[-ro,w/2]])
    c,s=math.cos(th),math.sin(th); Rm=np.array([[c,-s],[s,c]])
    return Polygon(pts@Rm.T+[x,y])
def kmax(v):
    wb,w,fo,ro,tr,rm=v; return 1/(math.sqrt(rm**2-wb**2)-tr/2)
NSEG=8
def rollout(xv,v,ds=0.15):
    km=kmax(v)
    # start: rear axle 8 m back from mouth, centred, heading into parcel
    p=mouth-ax*(8+v[0]); th=math.atan2(ax[1],ax[0]); x,y=p
    traj=[(x,y,th)]
    for i in range(NSEG):
        kap=xv[2*i]*km; Ls=xv[2*i+1]
        n=max(1,int(Ls/ds))
        for _ in range(n):
            d=Ls/n; x+=d*math.cos(th); y+=d*math.sin(th); th+=d*kap; traj.append((x,y,th))
    return traj
def cost(xv,v,A,Ap):
    tr=rollout(xv,v); bad=0.0
    for (x,y,th) in tr[::2]:
        b=body(x,y,th,v)
        if not Ap.contains(b): bad+=b.difference(A).area
    x,y,th=tr[-1]
    # goal: pointing back out, rear axle inside corridor region near mouth
    want=math.atan2(-ax[1],-ax[0]); dth=math.atan2(math.sin(th-want),math.cos(th-want))
    gx=mouth-ax*(4)    # rear axle ~4 m into corridor... front facing street
    pos=np.linalg.norm(np.array([x,y])-gx)
    return bad*20+abs(dth)*5+max(0,pos-2.5)*2
if __name__=='__main__':
    vname=sys.argv[1]; full=sys.argv[2]=='full'; v=VEH[vname]
    A=area(full); Ap=prep(A)
    b=[(-1,1),(0,12)]*NSEG
    best=None
    for seed in (1,2,3):
        r=differential_evolution(cost,b,args=(v,A,Ap),seed=seed,popsize=20,maxiter=300,tol=1e-9,polish=False)
        if best is None or r.fun<best.fun: best=r
        if r.fun<0.05: break
    tr=rollout(best.x,v)
    worst=max(b2.difference(A).area for b2 in (body(*p,v) for p in tr))
    clear=min(A.exterior.distance(body(*p,v)) if A.geom_type=='Polygon' else 0 for p in tr[::3])
    print(f'{vname:7s} paved={"full circle" if full else "own land only"}  cost={best.fun:.3f}  max body outside={worst:.3f} m2  path length={sum(best.x[1::2]):.1f} m')
    json.dump(dict(x=list(best.x),v=vname,full=full,cost=best.fun,worst=worst),open(f'turn/sim_{vname}_{sys.argv[2]}.json','w'))
