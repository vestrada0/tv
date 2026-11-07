import sys, math, json, numpy as np
sys.path.insert(0,'turn'); sys.path.insert(0,'.')
from sim import body, kmax, VEH, mouth, ax, corr, par, ring_full, island, m13, m20, R, k, P
from shapely.geometry import Point, MultiPoint, Polygon
from shapely.ops import unary_union
from shapely.prepared import prep
from scipy.optimize import differential_evolution
# drivable: circle + small fillet up to corner 20, clipped to parcel, plus the passage, minus island
fillet=MultiPoint([tuple(m13),tuple(m20)]).union(ring_full).convex_hull
def area(full):
    disk=fillet if full else fillet.intersection(par)
    return unary_union([disk,corr]).buffer(0.005).difference(island)
nrm=np.array([-ax[1],ax[0]])
# 3-phase steering: swing (k0), loop around island (k1), exit swing (k2); rate-limited steering
def profile(p,v):
    km=kmax(v); rate=km/1.5          # full lock from straight in 1.5 m of travel (slow manoeuvring)
    s0,k0,L0,k1,L1,k2,L2,s3=p
    k0*=km; k1*=km; k2*=km
    kn=[(0,0),(s0,0)]; s=s0; last=0
    for kk,LL in ((k0,L0),(k1,L1),(k2,L2),(0,s3)):
        s+=abs(kk-last)/rate; kn.append((s,kk)); s+=LL; kn.append((s,kk)); last=kk
    return kn
def rollout(p,v,ds=0.1):
    kn=profile(p,v); xs=[q[0] for q in kn]; ks=[q[1] for q in kn]
    pos=mouth-ax*(5+v[0]); th=math.atan2(ax[1],ax[0]); x,y=pos; tr=[(x,y,th,0.0)]; s=0.0
    while s<kn[-1][0]:
        kap=float(np.interp(s+ds/2,xs,ks)); x+=ds*math.cos(th); y+=ds*math.sin(th); th+=ds*kap; s+=ds; tr.append((x,y,th,kap))
    return tr
def evaluate(p,v,A,Ap):
    tr=rollout(p,v); bad=0.0; turned=0.0
    for q in tr[::3]:
        b=body(q[0],q[1],q[2],v)
        if not Ap.contains(b): bad+=b.difference(A).area
    x,y,th,_=tr[-1]; th0=tr[0][2]
    want=th0+math.pi  # net heading change must be a U-turn
    # require net rotation of about -pi (clockwise) or +pi; use unwrapped total
    net=th-th0
    dth=min(abs(net-math.pi),abs(net+math.pi))
    lat=abs((np.array([x,y])-mouth)@nrm); along=(np.array([x,y])-mouth)@ax
    return bad,dth,lat,along,tr
def cost(p,v,A,Ap):
    bad,dth,lat,along,_=evaluate(p,v,A,Ap)
    return bad*30+dth*5+lat*2+max(0,along+2)
if __name__=='__main__':
    vname=sys.argv[1]; full=sys.argv[2]=='full'; v=VEH[vname]; A=area(full); Ap=prep(A)
    b=[(0,10),(-1,1),(0,15),(-1,1),(0,45),(-1,1),(0,20),(0,10)]
    best=None
    for seed in (11,12):
        r=differential_evolution(cost,b,args=(v,A,Ap),seed=seed,popsize=25,maxiter=500,tol=1e-12,polish=True,mutation=(0.5,1.0),recombination=0.7)
        if best is None or r.fun<best.fun: best=r
    bad,dth,lat,along,tr=evaluate(best.x,v,A,Ap)
    worst=max(body(q[0],q[1],q[2],v).difference(A).area for q in tr)
    clear=min(A.boundary.distance(body(q[0],q[1],q[2],v)) for q in tr[::2])
    print(f'{vname:7s} {"full circle" if full else "own land"}: cost={best.fun:.3f} worst-outside={worst:.3f} m2 min-clearance={clear:.2f} m heading-err={math.degrees(dth):.1f}deg lat={lat:.2f} m path={len(tr)*0.1:.0f} m',flush=True)
    json.dump(dict(p=list(map(float,best.x)),v=vname,full=full,cost=float(best.fun),worst=worst,clear=clear),open(f'turn/sim3_{vname}_{sys.argv[2]}.json','w'))
