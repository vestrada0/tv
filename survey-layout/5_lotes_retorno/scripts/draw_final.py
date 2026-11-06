import sys, json, math
sys.path.insert(0,'../p2'); sys.path.insert(0,'..')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, Point
from shapely import affinity
from tee7 import lots
from tee5 import PS, toW, road, W
import geo2, ezdxf
r=json.load(open(sys.argv[1])); L=r['L']; v=r['v']; bay=(2.5,7.0) if r['bay'] else None
Ls,RD=lots(L,*v,bay=bay)
k=geo2.k
T=lambda g: affinity.affine_transform(g,[k,0,0,-k,0,0])
PW=T(geo2.parcel)
# outside passage to Calle Libertad (13-14-16-18-19-20)
B=geo2.B; ext={14:(864,860),16:(944,911),18:(1001,948),19:(959,1005)}
pas=T(Polygon([B[13],ext[14],ext[16],ext[18],ext[19],B[20]]))
names=['Lot 1','Lot 2','Lot 3','Lot 4','Lot 5']
fr=RD.boundary.difference(PS.boundary.buffer(0.05))
fig,ax=plt.subplots(figsize=(10,10))
cols=['#a1d99b','#c7e9c0','#74c476','#c7e9c0','#a1d99b']
info=[]
for i,(g,n) in enumerate(zip(Ls,names)):
    gw=toW(g); ax.fill(*gw.exterior.xy,fc=cols[i],ec='#222',lw=1)
    f=fr.intersection(g.buffer(0.05)).length
    c=gw.representative_point(); ax.text(c.x,c.y,f'{n}\n{g.area:.1f} m²\nfrente {f:.1f} m',ha='center',va='center',fontsize=10)
    info.append((n,g.area,f))
rw=toW(RD); 
for gg in getattr(rw,'geoms',[rw]): ax.fill(*gg.exterior.xy,fc='#bdbdbd',ec='#555',lw=1)
ax.fill(*pas.exterior.xy,fc='#e0e0e0',ec='#777',lw=1,hatch='..')
ax.plot(*PW.exterior.xy,color='k',lw=2)
c=rw.centroid
ax.text(*toW(Point(L-2.2,-W/2)).coords[0],'retorno\n(T)',ha='center',va='center',fontsize=8)
if bay: ax.text(*toW(Point(3.5,-W-1.25)).coords[0],'bahía',ha='center',va='center',fontsize=7)
pc=pas.centroid; ax.text(pc.x,pc.y,'paso existente\n4.1–5.0 m\na Calle Libertad',fontsize=7,ha='center',va='center',rotation=37)
ax.set_aspect('equal'); ax.axis('off')
tot=sum(a for _,a,_ in info)
ax.set_title(f'5 lotes · {tot:.0f} m² vendibles ({tot/PS.area*100:.0f}%) · vialidad {RD.area:.0f} m²\ncarril 4.06 m × {L:.0f} m + retorno en T (15 × 4.5 m) + bahía de espera 2.5 × 7 m',fontsize=11)
plt.tight_layout(); plt.savefig(sys.argv[2],dpi=130)
# DXF
doc=ezdxf.new(); msp=doc.modelspace()
for lay in ['PARCEL','LOTS','ROAD','LABELS']: doc.layers.add(lay)
msp.add_lwpolyline(list(PW.exterior.coords),dxfattribs={'layer':'PARCEL'})
for gg in getattr(rw,'geoms',[rw]): msp.add_lwpolyline(list(gg.exterior.coords),dxfattribs={'layer':'ROAD'})
for (n,a,f),g in zip(info,Ls):
    gw=toW(g); msp.add_lwpolyline(list(gw.exterior.coords),dxfattribs={'layer':'LOTS'})
    p=gw.representative_point(); msp.add_text(f'{n} {a:.2f} m2',dxfattribs={'layer':'LABELS','height':0.8}).set_placement((p.x,p.y))
doc.saveas(sys.argv[2].replace('.png','.dxf'))
# vertex table per lot (local metres)
with open(sys.argv[2].replace('.png','_lots.txt'),'w') as fh:
    for (n,a,f),g in zip(info,Ls):
        fh.write(f'{n}: {a:.2f} m2, frontage {f:.2f} m\n')
        cs=list(toW(g).exterior.coords)[:-1]
        for i in range(len(cs)):
            p,q=cs[i],cs[(i+1)%len(cs)]; fh.write(f'   side {i+1}: {math.dist(p,q):.2f} m\n')
for x in info: print(x)
print('road',RD.area,'parcel',PS.area)
