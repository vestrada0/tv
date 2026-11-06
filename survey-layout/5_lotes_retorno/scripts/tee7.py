import sys, math, json, numpy as np
from scipy.optimize import least_squares
from tee5 import PS, road, toW, W
from shapely.geometry import Polygon
def side(p,q,keep_left=True):
    # big polygon left of directed line p->q
    p=np.array(p,float);q=np.array(q,float); d=(q-p)/np.linalg.norm(q-p); n=np.array([-d[1],d[0]])
    if not keep_left: n=-n
    return Polygon([p-d*300,p+d*300,p+d*300+n*300,p-d*300+n*300])
def lots(L,x1,sN,sS,y,e,arm=5.5,hd=4.5,bay=(2.5,7.0)):
    RD=road(L,arm,hd,bay); R=PS.difference(RD)
    st=(L,e)
    north=Polygon([(-50,-W/2),(L,-W/2),st,(L+(40-L)*20,e+(y-e)*20),(L+(40-L)*20,300),(-50,300)]).intersection(R)
    south=R.difference(north)
    NE=north.intersection(Polygon([(-50,-300),(x1,-300),(x1,300),(-50,300)])); rest=north.difference(NE)
    A=side((L,arm),(sN,40),keep_left=False)     # left of upward line = west side
    NW=rest.intersection(A); NM=rest.difference(A)
    B=side((L,-W-arm),(sS,-40),keep_left=True) # west side of downward line
    SW=south.intersection(B); SE=south.difference(B)
    return [NE,NM,NW,SW,SE],RD
def metrics(L,v,**kw):
    Ls,RD=lots(L,*v,**kw)
    fr=RD.boundary.difference(PS.boundary.buffer(0.05))
    return [dict(area=g.area,front=fr.intersection(g.buffer(0.05)).length,cmp=g.length/math.sqrt(g.area),parts=len(getattr(g,'geoms',[g]))) for g in Ls],Ls,RD
def solve(L,e,**kw):
    A=(PS.area-road(L,**kw).area)/5
    f=lambda v:[(m['area']-A)/5 for m in metrics(L,list(v)+[e],**kw)[0][:4]]
    best=None
    for g in ([12,24,20,0],[12,22,24,5],[11,26,16,-5],[12,20,26,8]):
        try: r=least_squares(f,g,bounds=([0.5,-20,-20,-40],[60,80,80,40]))
        except Exception: continue
        if best is None or r.cost<best.cost: best=r
    v=list(best.x)+[e]; m,Ls,RD=metrics(L,v,**kw)
    return v,m,Ls,RD,best.cost
if __name__=='__main__':
    out={}
    for L in [float(a) for a in sys.argv[1:]]:
        rows=[]
        for e in np.arange(-8,4.1,1.0):
            try: v,m,Ls,RD,c=solve(L,e)
            except Exception: continue
            if c>0.05 or any(q['parts']!=1 for q in m): continue
            rows.append(dict(minf=min(q['front'] for q in m),maxc=max(q['cmp'] for q in m),v=[float(x) for x in v],m=m,road=RD.area,L=L))
        good=[r for r in rows if r['minf']>=6]
        pick=min(good,key=lambda r:r['maxc']) if good else (max(rows,key=lambda r:r['minf']) if rows else None)
        if pick:
            out[L]=pick
            print(f"L={L} road={pick['road']:.1f} feasible={len(good)}/{len(rows)} minf={pick['minf']:.1f} maxc={pick['maxc']:.2f} v={[round(x,1) for x in pick['v']]}",' | '.join(f"{q['area']:.0f} f{q['front']:.1f} c{q['cmp']:.2f}" for q in pick['m']),flush=True)
        else: print('L',L,'none',flush=True)
    json.dump(out,open('tee7_'+'_'.join(sys.argv[1:])+'.json','w'))
