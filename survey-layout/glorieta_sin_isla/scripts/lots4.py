import math, numpy as np, json, sys
from bulb import *
from lots2 import frontage_line, cutline
from shapely.ops import split
from scipy.optimize import brentq, minimize
PSI=0.62
def garage(Rb,sc,depth=7.0,area=49.0):
    RD=road(Rb,sc); R=PS.difference(RD)
    f=lambda w: R.intersection(box(-2,0,w,depth)).area-area
    w=brentq(f,1,20); return R.intersection(box(-2,0,w,depth)),w
def build(Rb,sc,cs,g1):
    RD=road(Rb,sc); R=PS.difference(RD).difference(g1); A=R.area/4
    fl=frontage_line(RD); T=fl.length
    c0=fl.project(Point(fl.intersection(g1.buffer(0.05)).coords[-1]) if fl.intersection(g1.buffer(0.05)).geom_type=='LineString' else Point(0,0))/T
    rest=R; out=[]; specs=[]; prev=c0
    for i,c in enumerate(cs):
        c=c0+(1-c0)*c
        P=np.array(fl.interpolate(c*T).coords[0]); O=np.array([sc,NC]); rad=math.atan2(P[1]-O[1],P[0]-O[0])
        q=Point(fl.interpolate((prev+c)/2*T).coords[0]).buffer(0.3)
        def piece(psi):
            parts=list(split(rest,cutline(P,rad+psi)).geoms)
            if len(parts)<2: return None,None
            lot=max(parts,key=lambda g:g.intersection(q).area)
            return lot,unary_union([g for g in parts if g is not lot])
        def f(psi):
            lot,_=piece(psi); return (lot.area-A) if lot is not None else float('nan')
        fa,fb=f(-PSI),f(PSI)
        if not (np.isfinite(fa) and np.isfinite(fb)) or fa*fb>0: return None,(min(abs(fa) if np.isfinite(fa) else 1e3,abs(fb) if np.isfinite(fb) else 1e3),i)
        psi=brentq(f,-PSI,PSI,xtol=1e-4); lot,rest=piece(psi); out.append(lot); specs.append((P.tolist(),rad+psi,psi)); prev=c
    out.append(rest)
    allL=[g1]+out
    frl=RD.boundary.difference(PS.boundary.buffer(0.05))
    m=[dict(area=g.area,front=frl.intersection(g.buffer(0.05)).length,cmp=g.length/math.sqrt(g.area),parts=len(getattr(g,'geoms',[g]))) for g in allL]
    return (allL,RD,m,specs),None
def design(Rb,sc,g1):
    def obj(x):
        cs=np.sort(np.clip(x,0.02,0.98)); r,err=build(Rb,sc,cs,g1)
        if r is None: return 100+err[0]/10+(3-err[1])*20
        m=r[2]
        if any(q['parts']>1 for q in m): return 50
        return -min(q['front'] for q in m[1:])+0.02*max(q['cmp'] for q in m[1:])
    best=None
    for x0 in ([0.25,0.5,0.75],[0.3,0.55,0.78],[0.2,0.45,0.7],[0.35,0.55,0.72]):
        r=minimize(obj,x0,method='Nelder-Mead',options=dict(maxiter=200,xatol=1e-3,fatol=1e-3))
        if best is None or r.fun<best.fun: best=r
    cs=np.sort(np.clip(best.x,0.02,0.98)); res,_=build(Rb,sc,cs,g1); return cs,res
if __name__=='__main__':
    Rb=float(sys.argv[1]); e=float(sys.argv[2]); sc=Rb+e
    g1,w=garage(Rb,sc)
    cs,res=design(Rb,sc,g1)
    L,RD,m,specs=res
    print(f'Ø{2*Rb:.1f} neck+{e}: garage lot width {w:.2f} m; road {RD.area:.0f} m2; lots',' | '.join(f"{q['area']:.1f} f{q['front']:.1f} c{q['cmp']:.2f}" for q in m),' tilts',[round(math.degrees(s[2])) for s in specs],flush=True)
    json.dump(dict(Rb=Rb,e=e,cs=list(map(float,cs)),w=w),open(f'lots4_{Rb}_{e}.json','w'))
