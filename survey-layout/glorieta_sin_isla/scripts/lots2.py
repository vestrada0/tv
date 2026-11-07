import math, numpy as np
from bulb import *
from shapely.ops import split, linemerge
from scipy.optimize import brentq
def frontage_line(RD):
    fr=RD.boundary.difference(PS.boundary.buffer(0.05))
    fr=linemerge(fr) if fr.geom_type=='MultiLineString' else fr
    if fr.geom_type=='MultiLineString': fr=max(fr.geoms,key=lambda g:g.length)
    # orient: start at the north side of the neck (n near 0 at small s)
    a,b=Point(fr.coords[0]),Point(fr.coords[-1])
    if a.y<b.y: fr=LineString(list(fr.coords)[::-1])
    return fr
def cutline(Pt,ang):
    d=np.array([math.cos(ang),math.sin(ang)]); return LineString([Pt-d*0.3,Pt+d*80])
def lots(Rb,sc,off=0.0,fr_weights=None):
    RD=road(Rb,sc,off); R=PS.difference(RD); O=np.array([sc,NC+off]); A=R.area/5
    fl=frontage_line(RD); T=fl.length
    w=fr_weights or [1]*5; cum=np.cumsum(w)/sum(w)
    rest=R; out=[]; specs=[]
    for i in range(4):
        P=np.array(fl.interpolate(cum[i]*T).coords[0])
        rad=math.atan2(P[1]-O[1],P[0]-O[0])
        def piece(psi):
            L=cutline(P,rad+psi); parts=list(split(rest,L).geoms)
            if len(parts)<2: return None,None
            # the lot is the piece that contains the start of the frontage segment for this lot
            q=Point(fl.interpolate(max(0,(cum[i]-w[i]/sum(w)/2))*T).coords[0]).buffer(0.3)
            lot=max(parts,key=lambda g:g.intersection(q).area)
            return lot,unary_union([g for g in parts if g is not lot])
        def f(psi):
            lot,_=piece(psi)
            return (lot.area-A) if lot is not None else 1e3
        grid=np.linspace(-1.2,1.2,25); vals=[f(g) for g in grid]
        root=None
        for a_,b_,fa,fb in zip(grid[:-1],grid[1:],vals[:-1],vals[1:]):
            if fa*fb<0 and abs(fa)<500 and abs(fb)<500:
                r_=brentq(f,a_,b_,xtol=1e-4)
                if root is None or abs(r_)<abs(root): root=r_
        if root is None: return None
        lot,rest=piece(root); out.append(lot); specs.append((P,rad+root))
    out.append(rest)
    frl=RD.boundary.difference(PS.boundary.buffer(0.05))
    m=[dict(area=g.area,front=frl.intersection(g.buffer(0.05)).length,cmp=g.length/math.sqrt(g.area),parts=len(getattr(g,'geoms',[g]))) for g in out]
    return out,RD,m,specs
if __name__=='__main__':
    for Rb in (6.75,7.75,8.25):
        for e in (0.3,2.0,4.0,6.0):
            r=lots(Rb,Rb+e)
            if r is None: print(Rb,e,'no solution'); continue
            L,RD,m,_=r
            print(f'Rb={Rb} neck+{e}: road {RD.area:.0f}  lots',' | '.join(f"{q['area']:.0f} f{q['front']:.1f} c{q['cmp']:.2f}{'' if q['parts']==1 else ' SPLIT'}" for q in m),flush=True)
