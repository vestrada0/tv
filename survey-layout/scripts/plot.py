import json,sys,math
sys.path.insert(0,'..')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely.geometry import shape
from geo import lots as cur_lots, circ, parcel as ppx
X=json.load(open('xform.json')); k,ox,oy=X['k'],X['ox'],X['oy']
from shapely import affinity
def tom(g): return affinity.affine_transform(g,[k,0,0,-k,-ox*k,oy*k])
P=shape(json.load(open('parcel.geojson'))['features'][0]['geometry'])
def draw(ax,polys,title):
    ax.plot(*P.exterior.xy,color='k',lw=1.5)
    for g,fc,lab in polys:
        for gg in getattr(g,'geoms',[g]):
            ax.fill(*gg.exterior.xy,fc=fc,ec='#333',lw=.7,alpha=.85)
        if lab: c=g.representative_point(); ax.text(c.x,c.y,lab,ha='center',va='center',fontsize=7.5)
    ax.set_aspect('equal'); ax.set_title(title,fontsize=10); ax.axis('off')
fig,axs=plt.subplots(1,3,figsize=(18,7))
cur=[(tom(l),'#9ecae1',f'{tom(l).area:.0f} m²') for l in cur_lots()]
cur.append((tom(ppx.intersection(circ)),'#bbb','turnaround\n%.0f m²'%tom(ppx.intersection(circ)).area))
draw(axs[0],cur,'Your current plan (Opción 2)\n5 lots · 1,254 m² saleable · 308 m² road')
for ax,f,t in [(axs[1],'out/A_lot120_road6_single_road.geojson','subdivision-agent, rules A (≥120 m² lots, 6 m road)'),
               (axs[2],'out/B_lot160_road8_single_road.geojson','subdivision-agent, rules B (≥160 m² lots, 8 m road)')]:
    d=json.load(open(f)); polys=[]
    for ft in d['features']:
        pr=ft['properties']; g=shape(ft['geometry'])
        if pr['layer']=='roads': polys.append((g,'#bbb','road\n%.0f m²'%g.area))
        if pr['layer']=='lots':
            fc='#a1d99b' if pr['passes_all'] else ('#fdae6b' if pr['lot_type']=='remainder' else '#fc9272')
            polys.append((g,fc,f"{pr['area_sqm']:.0f}"+('' if pr['passes_all'] else ('\nleftover' if pr['lot_type']=='remainder' else '\n✗'))))
    s=json.load(open('out/summary.json')); 
    draw(ax,polys,t)
fig.text(0.5,0.02,'green = passes the rules · red = slightly under minimum · orange = leftover with no road access · grey = road',ha='center',fontsize=9)
plt.tight_layout(); plt.savefig('compare.png',dpi=110)
