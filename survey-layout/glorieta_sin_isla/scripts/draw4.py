import sys, json, math, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from bulb import *
from lots4 import build, garage
from quick import balloon
import ezdxf
Rb,e=7.75,7.0; sc=Rb+e; cfg=json.load(open('lots4_7.75_7.0.json'))
g1,w=garage(Rb,sc); (L,RD,m,specs),_=build(Rb,sc,cfg['cs'],g1)
fig,ax=plt.subplots(figsize=(11,11))
cols=['#fdd49e','#a1d99b','#c7e9c0','#74c476','#c7e9c0']
for i,(g,q) in enumerate(zip(L,m)):
    gw=toW(g); ax.fill(*gw.exterior.xy,fc=cols[i],ec='#222',lw=1)
    c=gw.representative_point()
    lab=f'Lote 1\ncochera 2 autos\n{q["area"]:.0f} m²' if i==0 else f'Lote {i+1}\n{q["area"]:.1f} m²\nfrente {q["front"]:.1f} m'
    ax.text(c.x,c.y,lab,ha='center',va='center',fontsize=8 if i==0 else 10)
rw=toW(RD); ax.fill(*rw.exterior.xy,fc='#bdbdbd',ec='#444',lw=1.2)
pw=toW(PASS); ax.fill(*pw.exterior.xy,fc='#e0e0e0',ec='#777',hatch='..',lw=1)
ax.plot(*toW(PS).exterior.xy,color='k',lw=2)
cc=toW(Point(sc,NC)); ax.text(cc.x,cc.y,f'glorieta sin isla\nØ {2*Rb:.1f} m',ha='center',va='center',fontsize=9)
q=json.load(open(sys.argv[1])) if len(sys.argv)>1 else {}
colv={'car':'#08519c','pickup':'#d94801','van':'#6a51a3'}; names={'car':'auto','pickup':'pickup','van':'van'}
for vn in ('pickup',):
    if vn not in q: continue
    v=VEH[vn]; pts=balloon(v,sc,q[vn]['r'],q[vn]['ra'])
    xs=[toW(Point(x,y)).x for x,y,t in pts]; ys=[toW(Point(x,y)).y for x,y,t in pts]
    ax.plot(xs,ys,color=colv[vn],lw=1.5,ls='--',label=f'pickup: vuelta en U completa, holgura mínima {q[vn]["clr"]*100:.0f} cm')
    for p_ in pts[40:-40:12]:
        b=toW(body(p_[0],p_[1],p_[2],v)); ax.plot(*b.exterior.xy,color=colv[vn],lw=.6,alpha=.6)
pc=pw.centroid; ax.text(pc.x,pc.y,'paso existente\na Calle Libertad',fontsize=8,ha='center',va='center',rotation=-35)
tot=sum(x['area'] for x in m)
ax.set_title(f'Cochera + 4 lotes con glorieta sin isla · {tot:.0f} m² vendibles ({tot/PS.area*100:.0f}%) · vialidad {RD.area:.0f} m²',fontsize=12)
if q: ax.legend(loc='lower left',fontsize=9)
ax.set_aspect('equal'); ax.axis('off'); plt.tight_layout(); plt.savefig('cochera_glorieta.png',dpi=130)
doc=ezdxf.new(); msp=doc.modelspace()
for lay in ['PARCEL','LOTS','ROAD','LABELS']: doc.layers.add(lay)
msp.add_lwpolyline(list(toW(PS).exterior.coords),dxfattribs={'layer':'PARCEL'})
msp.add_lwpolyline(list(rw.exterior.coords),dxfattribs={'layer':'ROAD'})
with open('cochera_glorieta_lotes.txt','w') as fh:
    fh.write(f'Glorieta sin isla diametro {2*Rb:.1f} m; entrada recta de {e:.1f} m (ancho 4.06 m); vialidad {RD.area:.1f} m2\n')
    for i,(g,x) in enumerate(zip(L,m)):
        gw=toW(g); msp.add_lwpolyline(list(gw.exterior.coords),dxfattribs={'layer':'LOTS'})
        p=gw.representative_point(); msp.add_text(f'Lote {i+1} {x["area"]:.2f} m2',dxfattribs={'layer':'LABELS','height':0.8}).set_placement((p.x,p.y))
        fh.write(f'Lote {i+1}: {x["area"]:.2f} m2, frente {x["front"]:.2f} m\n')
        cs_=list(gw.exterior.coords)[:-1]
        for j in range(len(cs_)):
            a,b=cs_[j],cs_[(j+1)%len(cs_)]; d=math.dist(a,b)
            if d>0.3: fh.write(f'    lado {j+1}: {d:.2f} m\n')
doc.saveas('cochera_glorieta.dxf'); print('total',round(tot,1),'road',round(RD.area,1),'garage width',round(w,2))
