import sys, math, json, numpy as np
from scipy.optimize import least_squares
from five import PAR, p13, u, nrm, k
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from shapely import affinity
nn=-nrm
O=p13
def toS(g):  # world -> (s,n)
    return affinity.affine_transform(g,[u[0],u[1],nn[0],nn[1],-float(O@u),-float(O@nn)])
def toW(g):
    # inverse: x = O + s*u + n*nn
    return affinity.affine_transform(g,[u[0],nn[0],u[1],nn[1],O[0],O[1]])
PS=toS(PAR)
W=4.061; 
def road(L,arm=5.5,hd=4.5,bay=(2.5,7.0)):
    parts=[Polygon([(-1,0),(L,0),(L,-W),(-1,-W)])]
    if arm: parts.append(Polygon([(L-hd,arm),(L,arm),(L,-W-arm),(L-hd,-W-arm)]))
    if bay: bw,bl=bay; parts.append(Polygon([(0,-W),(bl,-W),(bl,-W-bw),(0,-W-bw)]))
    return unary_union(parts).intersection(PS)
def lots(L,x1,x2,y1,y2,arm=5.5,hd=4.5,bay=(2.5,7.0)):
    RD=road(L,arm,hd,bay); R=PS.difference(RD)
    big=200
    top=(L,arm if arm else 0); bot=(L,-W-(arm if arm else 0))
    Wl=Polygon([top,(big,y1+(y1-top[1])*0 ),(big,y2),bot]) if False else None
    # splitters: straight from head corners to far west (s=60) at heights y1,y2 (measured at s=40)
    def ext(p,y): # line from p through (40,y) to s=80
        s0,n0=p; m=(y-n0)/(40-s0); return (80, n0+m*(80-s0))
    WL=Polygon([top,ext(top,y1),ext(bot,y2),bot]).intersection(R)
    north=Polygon([(-50,0),(L,0),top,ext(top,y1),(80,200),(-50,200)]).intersection(R).difference(WL)
    south=R.difference(north).difference(WL)
    NE=north.intersection(Polygon([(-50,-1),(x1,-1),(x1,200),(-50,200)])); NW=north.difference(NE)
    SE=south.intersection(Polygon([(-50,1),(x2,1),(x2,-200),(-50,-200)])); SW=south.difference(SE)
    return [NE,NW,WL,SW,SE],RD
def metrics(L,v,**kw):
    Ls,RD=lots(L,*v,**kw)
    fr=RD.boundary.difference(PS.boundary.buffer(0.05))
    return [dict(area=g.area,front=fr.intersection(g.buffer(0.05)).length,cmp=g.length/math.sqrt(g.area),parts=len(getattr(g,'geoms',[g]))) for g in Ls],RD
def solve(L,**kw):
    A=(PS.area-road(L,**kw).area)/5
    f=lambda v:[ (m['area']-A)/10 for m in metrics(L,v,**kw)[0][:4]]
    r=least_squares(f,[11.6,10,8,-9],bounds=([0.5,0.5,-11,-25],[L-0.5,L+20,22,0]))
    m,RD=metrics(L,r.x,**kw)
    return r.x,m,RD
if __name__=='__main__':
    for L in [float(a) for a in sys.argv[1:]]:
        v,m,RD=solve(L)
        print(f"L={L:4.1f} road={RD.area:5.1f} v={[round(x,2) for x in v]} ",' | '.join(f"{q['area']:.0f} f{q['front']:.1f} c{q['cmp']:.2f}{'' if q['parts']==1 else ' SPLIT'}" for q in m))
