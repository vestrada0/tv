import json,sys,math
sys.path.insert(0,'.'); sys.path.insert(0,'..')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely import affinity
from shapely.ops import unary_union
import geo2
import geo as g1
def tf(g,k): return affinity.affine_transform(g,[k,0,0,-k,0,0])
fig,axs=plt.subplots(1,2,figsize=(15,7.8))
def draw(ax,par,items,title,trees=()):
    for g,fc,lab in items:
        for gg in getattr(g,'geoms',[g]):
            if gg.area<2: continue
            ax.fill(*gg.exterior.xy,fc=fc,ec='#333',lw=.8)
        if lab: c=max(getattr(g,'geoms',[g]),key=lambda x:x.area).representative_point(); ax.text(c.x,c.y,lab,ha='center',va='center',fontsize=9)
    ax.plot(*par.exterior.xy,color='k',lw=1.8)
    for t in trees: ax.add_patch(plt.Circle(t,1.4,fc='#31a354',ec='#006d2c',alpha=.8))
    ax.set_aspect('equal'); ax.set_title(title,fontsize=11); ax.axis('off')
k1=0.07032598126928438
L1=[(tf(l,k1),'#9ecae1',f'{tf(l,k1).area:.0f} m²') for l in g1.lots()]
L1.append((tf(g1.parcel.intersection(g1.circ),k1),'#cfcfcf','turnaround\n~308 m²'))
draw(axs[0],tf(g1.parcel,k1),L1,'Opción 2 – circular turnaround\n5 lots · 1,254 m² saleable (80%) · lots 131–376 m²')
k2=geo2.k
L2=[(tf(geo2.lots[a],k2),'#a1d99b',f'{a:.2f} m²') for a in geo2.Am]
lane=geo2.parcel.difference(unary_union(list(geo2.lots.values())))
L2.append((tf(lane,k2),'#cfcfcf',''))
trees=[(x*k2,-y*k2) for x,y in json.load(open('trees.json'))]
draw(axs[1],tf(geo2.parcel,k2),L2,'Raúl Ruiz de Haro project – straight lane\n6 lots · 1,414.66 m² saleable (90%) · lots 232–238 m²',trees)
c=tf(lane,k2); cc=max(c.geoms,key=lambda x:x.area).centroid
axs[1].annotate('lane 4.0 m wide · 155 m²\n(+23.6 m passage to Calle Libertad)',xy=(cc.x,cc.y),xytext=(cc.x+8,cc.y-24),fontsize=9,arrowprops=dict(arrowstyle='->'))
fig.text(0.5,0.03,'Same parcel: 1,570 m². Green circles = existing trees (from the plan).',ha='center',fontsize=9)
plt.tight_layout(); plt.savefig('compare2.png',dpi=110)
