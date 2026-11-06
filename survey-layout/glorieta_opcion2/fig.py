import sys, math, numpy as np
sys.path.insert(0,'.')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely import affinity
from shapely.geometry import Point
from geo import P, C, R, Rin, parcel, lots
k=0.07032598126928438
T=lambda g: affinity.affine_transform(g,[k,0,0,-k,-C[0]*k,C[1]*k])   # centre at origin, metres
par=T(parcel); fig,ax=plt.subplots(figsize=(8,8))
for l in lots():
    g=T(l); ax.fill(*g.exterior.xy,fc='#eef3f8',ec='#999',lw=.6)
ax.plot(*par.exterior.xy,color='k',lw=1.5)
def ring(r1,r2,fc,a,lab):
    g=Point(0,0).buffer(r2,256).difference(Point(0,0).buffer(r1,256)).intersection(par)
    for gg in getattr(g,'geoms',[g]): ax.fill(*gg.exterior.xy,fc=fc,alpha=a,ec='none',label=lab); lab=None
    for gg in getattr(g,'geoms',[g]):
        for i in gg.interiors: pass
ax.add_patch(plt.Circle((0,0),R*k,fc='#d9d9d9',ec='#555',lw=1,zorder=0))
ring(4.3,9.60,'#fb6a4a',.25,'camión ~8 m: necesita hasta r 9.6 m')
ring(4.3,7.56,'#fd8d3c',.45,'pickup / SUV: r 4.3–7.6 m')
ring(4.3,7.08,'#31a354',.55,'auto: r 4.3–7.1 m')
ax.add_patch(plt.Circle((0,0),Rin*k,fc='#8c8c8c',ec='k',lw=1,zorder=5))
ax.add_patch(plt.Circle((0,0),7.34,fc='none',ec='k',ls='--',lw=1,zorder=6))
# outside-parcel part of circle
out=Point(0,0).buffer(R*k,256).difference(par)
for gg in getattr(out,'geoms',[out]): ax.fill(*gg.exterior.xy,fc='none',ec='#d62728',hatch='////',lw=1,zorder=7)
ax.annotate('parte del círculo fuera del predio\n(terreno de Francisco Flores) ≈ 20 m²',xy=(7.6,-1.5),xytext=(9,6),fontsize=8,color='#d62728',arrowprops=dict(arrowstyle='->',color='#d62728'))
ax.annotate('aquí el anillo sólo mide 4.0 m\n(lindero a 7.97 m del centro)',xy=(6.2,1.8),xytext=(9,1),fontsize=8,arrowprops=dict(arrowstyle='->'))
ax.text(0,0,'isla\nr 4.0 m',ha='center',va='center',fontsize=8,color='w',zorder=8)
ax.set_xlim(-13,17); ax.set_ylim(-13,13); ax.set_aspect('equal'); ax.axis('off')
ax.legend(loc='lower left',fontsize=8)
ax.set_title('Opción 2: glorieta Ø 20.4 m con isla Ø 8 m\n¿Puede dar la vuelta completa?',fontsize=11)
plt.tight_layout(); plt.savefig('turn/glorieta.png',dpi=130)
