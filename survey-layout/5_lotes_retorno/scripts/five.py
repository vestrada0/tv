import sys, math, json, numpy as np
sys.path.insert(0,'../p2'); import geo2
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import split
from shapely import affinity
k=geo2.k
T=lambda g: affinity.affine_transform(g,[k,0,0,-k,0,0])
PAR=T(geo2.parcel)
P=lambda x,y: np.array([x*k,-y*k])
p13=P(724,768); p20=P(691.8,811.8)
u=P(297,478)-p13; u/=np.linalg.norm(u)
v=p20-p13                    # across lane (N->S)
nrm=np.array([-u[1],u[0]]);  nrm = nrm if np.dot(nrm,v)>0 else -nrm   # points south
W=abs(np.dot(v,nrm))
dN=P(408.8,553.8)-P(564.5,281.2); dN/=np.linalg.norm(dN)   # north dividers (pointing toward lane)
dS=P(421.5,852.8)-P(533.3,703.8); dS/=np.linalg.norm(dS)   # south divider (away from lane)
def lane(L): return Polygon([p13,p13+u*L,p20+u*L,p20])
def halfplane(pt,d,side_pt):
    # big polygon on side of infinite line (pt,d) containing side_pt
    n=np.array([-d[1],d[0]]); 
    if np.dot(side_pt-pt,n)<0: n=-n
    return Polygon([pt-d*500,pt+d*500,pt+d*500+n*500,pt-d*500+n*500])
def layout(L,phi,t1,t2,t3,nN=3):
    R=PAR.difference(lane(L))
    c=(p13+p20)/2+u*L        # lane end centre
    d=np.array([math.cos(phi),math.sin(phi)]) # west splitter direction
    # north/south split: lane centreline up to end, then splitter ray
    cl=Polygon()  # build north region polygon as halfplanes
    north_sp=p13-nrm*1             # a point north of lane
    Hn1=halfplane((p13+p20)/2,u,north_sp).intersection(halfplane(c,np.array([-u[1],u[0]]),c-u*5))  # north of centreline, east of end
    Hn2=halfplane(c,d,c-nrm*3+u*0.0).difference(halfplane(c,np.array([-u[1],u[0]]),c-u*5))         # beyond end, north of splitter
    Nreg=R.intersection(Hn1.union(Hn2)); Sreg=R.difference(Nreg)
    def cutrow(reg,ts,dvec,edge0,side):
        pieces=[]; rest=reg
        for t in ts:
            pt=edge0+u*t
            H=halfplane(pt,dvec,pt-u*5)       # east of divider
            pieces.append(rest.intersection(H)); rest=rest.difference(H)
        pieces.append(rest); return pieces
    N=cutrow(Nreg,[t1,t2][:nN-1],dN,p13,'N')
    S=cutrow(Sreg,[t3],dS,p20,'S')
    return N,S
def frontage(g,L):
    edge=LineString([p13,p13+u*L,p20+u*L,p20]); return edge.intersection(g.buffer(0.05)).length
def bis(f,lo,hi,n=60):
    flo=f(lo)
    for _ in range(n):
        m=(lo+hi)/2; fm=f(m)
        if (fm>0)==(flo>0): lo,flo=m,fm
        else: hi=m
    return (lo+hi)/2
def solve(L):
    A=(PAR.area-lane(L).area)/5
    base=math.atan2(u[1],u[0])
    phi=bis(lambda ph: layout(L,ph,1,2,1)[0][0].union(layout(L,ph,1,2,1)[0][1]).union(layout(L,ph,1,2,1)[0][2]).area-3*A, base-1.4, base+1.4)
    t1=bis(lambda t: layout(L,phi,t,t+0.1,1)[0][0].area-A, -20, L+20)
    t2=bis(lambda t: layout(L,phi,t1,t,1)[0][1].area-A, t1, L+25)
    t3=bis(lambda t: layout(L,phi,t1,t2,t)[1][0].area-A, -20, L+25)
    N,S=layout(L,phi,t1,t2,t3)
    lots=N+S
    return dict(L=L,phi=phi,t=(t1,t2,t3),road=lane(L).area,lots=[dict(area=g.area,front=frontage(g,L),cmp=g.length/math.sqrt(g.area),parts=len(getattr(g,'geoms',[g]))) for g in lots]),lots
if __name__=='__main__':
    for L in [float(a) for a in sys.argv[1:]]:
        r,_=solve(L)
        print(f"L={L:5.1f} road={r['road']:5.1f} lot={r['lots'][0]['area']:.1f} t={[round(x,1) for x in r['t']]} ", ' | '.join(f"f{q['front']:.1f} c{q['cmp']:.2f} p{q['parts']}" for q in r['lots']))
