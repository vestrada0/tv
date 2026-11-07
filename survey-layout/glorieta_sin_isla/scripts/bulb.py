import sys, math, json, numpy as np
D='/tmp/claude-0/-home-user-tv/81092d07-51e3-5619-a328-3c511eb7af2a/scratchpad'
sys.path.insert(0,D+'/opt'); sys.path.insert(0,D+'/p2')
from tee5 import PS, toS, toW, W
from five import T
import geo2
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely.prepared import prep
B=geo2.B; ext={14:(864,860),16:(944,911),18:(1001,948),19:(959,1005)}
PASS=toS(T(Polygon([B[13],ext[14],ext[16],ext[18],ext[19],B[20]])))
cs=list(PASS.exterior.coords)
m_in=np.array([(cs[0][0]+cs[5][0])/2,(cs[0][1]+cs[5][1])/2])     # mouth at parcel (13-20)
m_out=np.array([(cs[3][0]+cs[4][0])/2,(cs[3][1]+cs[4][1])/2])    # mouth at street (18-19)
pax=(m_in-m_out)/np.linalg.norm(m_in-m_out)                       # passage direction, into parcel
NC=-W/2                                                            # lane centreline n
def road(Rb,sc,off=0.0):
    disk=Point(sc,NC+off).buffer(Rb,256)
    neck=box(-2,-W,sc,0)
    return unary_union([disk,neck]).intersection(PS)
def drivable(Rb,sc,off=0.0):
    return unary_union([road(Rb,sc,off),PASS]).buffer(0.005)
VEH={'car':(2.70,1.80,0.90,1.00,1.55,5.5),'pickup':(3.30,1.95,0.95,1.30,1.65,6.3),'van':(3.67,2.02,1.00,1.20,1.73,6.5),
     'truck':(5.00,2.50,1.50,1.50,2.10,8.5)}
def body(x,y,th,v):
    wb,w,fo,ro,tr,rm=v
    pts=np.array([[-ro,-w/2],[wb+fo,-w/2],[wb+fo,w/2],[-ro,w/2]]); c,s=math.cos(th),math.sin(th)
    return Polygon(pts@np.array([[c,s],[-s,c]])+[x,y])
def kmax(v): wb,w,fo,ro,tr,rm=v; return 1/(math.sqrt(rm**2-wb**2)-tr/2)
def profile(p,v):
    km=kmax(v); rate=km/1.5
    s0,k0,L0,k1,L1,k2,L2,s3=p
    kn=[(0,0),(s0,0)]; s=s0; last=0
    for kk,LL in ((k0*km,L0),(k1*km,L1),(k2*km,L2),(0,s3)):
        s+=abs(kk-last)/rate; kn.append((s,kk)); s+=max(LL,0); kn.append((s,kk)); last=kk
    return kn
def rollout(p,v,ds=0.1):
    kn=profile(p,v); xs=[q[0] for q in kn]; ks=[q[1] for q in kn]
    pos=m_in-pax*(5+v[0]); th=math.atan2(pax[1],pax[0]); x,y=pos; tr=[(x,y,th)]; s=0.0
    while s<kn[-1][0]:
        kap=float(np.interp(s+ds/2,xs,ks)); x+=ds*math.cos(th); y+=ds*math.sin(th); th+=ds*kap; s+=ds; tr.append((x,y,th))
    return tr
def evaluate(p,v,A,Ap,step=3):
    tr=rollout(p,v); bad=0.0; clr=9.0
    for q in tr[::step]:
        b=body(*q,v)
        if not Ap.contains(b): bad+=b.difference(A).area; clr=min(clr,-b.difference(A).area)
        else: clr=min(clr,A.boundary.distance(b))
    x,y,th=tr[-1]; th0=tr[0][2]; net=th-th0
    dth=min(abs(net-math.pi),abs(net+math.pi))
    nn=np.array([-pax[1],pax[0]]); lat=abs((np.array([x,y])-m_in)@nn); along=(np.array([x,y])-m_in)@pax
    return bad,dth,lat,along,clr
