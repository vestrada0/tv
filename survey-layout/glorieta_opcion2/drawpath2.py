import sys, math, json, numpy as np
sys.path.insert(0,'turn'); sys.path.insert(0,'.')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from sim3 import area, body, VEH, rollout, mouth, ax
from sim import par, island, ring_full
from shapely.ops import unary_union
R=json.load(open('turn/refine.json'))
fig,axs=plt.subplots(1,2,figsize=(15,8.2))
for ax_,(vn,title) in zip(axs,[('car','Auto'),('pickup','Pickup / camioneta')]):
    c0,p,_,_=R[f'{vn}_own']; v=VEH[vn]; A=area(False)
    for g in getattr(A,'geoms',[A]): ax_.fill(*g.exterior.xy,fc='#e6e6e6',ec='#555',lw=1)
    out=ring_full.difference(par)
    for g in getattr(out,'geoms',[out]): ax_.fill(*g.exterior.xy,fc='none',ec='#d62728',hatch='////',lw=.8)
    ax_.fill(*island.exterior.xy,fc='#8c8c8c',ec='k'); ax_.plot(*par.exterior.xy,color='k',lw=1.6)
    tr=rollout(p,v); bodies=[]; mind=9; worst=None
    for i,q in enumerate(tr):
        b=body(q[0],q[1],q[2],v); bodies.append(b)
        if i%6==0: ax_.plot(*b.exterior.xy,color='#3182bd',lw=.45,alpha=.6)
        d=A.boundary.distance(b)
        if d<mind: mind=d; worst=b
    sw=unary_union(bodies)
    for g in getattr(sw,'geoms',[sw]): ax_.plot(*g.exterior.xy,color='#08519c',lw=1.3)
    ax_.plot([q[0] for q in tr],[q[1] for q in tr],color='#08519c',ls='--',lw=1)
    ax_.fill(*worst.exterior.xy,fc='#fb6a4a',ec='#a50f15',alpha=.85,lw=1.2)
    cc=worst.centroid
    ax_.annotate(f'punto más justo: {mind*100:.0f} cm\n(esquina 13: paso ↔ lindero)',xy=(cc.x,cc.y),xytext=(cc.x+5,cc.y-5),fontsize=9,color='#a50f15',arrowprops=dict(arrowstyle='->',color='#a50f15'))
    m=mouth-ax*7; ax_.text(m[0],m[1],'entrada / salida\npaso 4.1 m',fontsize=8,ha='center',rotation=-35)
    ax_.set_xlim(-14,16); ax_.set_ylim(-18,13); ax_.set_aspect('equal'); ax_.axis('off')
    ax_.set_title(f'{title}: holgura mínima {mind*100:.0f} cm',fontsize=12)
plt.suptitle('Opción 2: entrar, rodear la isla en sentido horario y salir de frente\n(volante gradual, conductor preciso, pavimento sólo dentro del predio; achurado rojo = terreno del vecino)',fontsize=11,y=0.995)
plt.tight_layout(rect=(0,0,1,0.92)); plt.savefig('turn/recorrido.png',dpi=120); print('ok')
