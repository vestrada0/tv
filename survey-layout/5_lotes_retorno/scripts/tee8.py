import sys, math, json, numpy as np
from scipy.optimize import differential_evolution
from tee7 import lots, PS
def evalv(v,L,bay):
    x1,sN,sS,y,e=v
    try: Ls,RD=lots(L,x1,sN,sS,y,e,bay=bay)
    except Exception: return 1e6,None
    fr=RD.boundary.difference(PS.boundary.buffer(0.05))
    m=[]
    for g in Ls:
        if g.is_empty or g.area<1: return 1e6,None
        m.append(dict(area=g.area,front=fr.intersection(g.buffer(0.05)).length,cmp=g.length/math.sqrt(g.area),parts=len(getattr(g,'geoms',[g]))))
    A=np.mean([q['area'] for q in m])
    f=sum(((q['area']-A)/A)**2 for q in m)*300
    f+=sum(max(0,6-q['front'])**2 for q in m)*3
    f+=sum((q['parts']-1) for q in m)*30
    f+=sum(max(0,q['cmp']-4.3) for q in m)*2
    return f,(m,RD.area)
def obj(v,L,bay): return evalv(v,L,bay)[0]
if __name__=='__main__':
    L=float(sys.argv[1]); bay=(2.5,7.0) if sys.argv[2]=='bay' else None
    b=[(4,20),(10,150),(0,150),(-12,22),(-9.5,5.5)]
    r=differential_evolution(obj,b,args=(L,bay),seed=3,popsize=25,maxiter=250,tol=1e-8,polish=False)
    f,(m,road)=evalv(r.x,L,bay)
    out=dict(L=L,bay=bool(bay),v=list(map(float,r.x)),f=float(f),road=road,m=m)
    json.dump(out,open(f'tee8_L{L}_{sys.argv[2]}.json','w'))
    print(f"L={L} {sys.argv[2]} f={f:.3f} road={road:.1f} v={[round(x,2) for x in r.x]}",' | '.join(f"{q['area']:.0f} f{q['front']:.1f} c{q['cmp']:.2f} p{q['parts']}" for q in m),flush=True)
