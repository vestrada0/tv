import json,math,sys
sys.path.insert(0,'.')
from geo import *
ls=lots(); Am=[375.70,267.70,259.20,221.30,130.58]
Ap=[p.area for p in ls]
k=math.sqrt(sum(a*b for a,b in zip(Am,Ap))/sum(b*b for b in Ap))
print('k m/px',k)
for a,b in zip(Am,Ap): print(a, round(b*k*k,1), f'{(b*k*k-a)/a*100:+.1f}%')
ox,oy=P[26]
T=lambda xy:(round((xy[0]-ox)*k,3), round(-(xy[1]-oy)*k,3))
ring=[T(P[i]) for i in order]; ring.append(ring[0])
mid=T(((P[13][0]+P[20][0])/2,(P[13][1]+P[20][1])/2))
# inward direction: perpendicular to 13-20, pointing into parcel (toward circle center)
c=T(C); dx,dy=c[0]-mid[0],c[1]-mid[1]; n=math.hypot(dx,dy)
gj={"type":"FeatureCollection","crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:EPSG::32613"}},
 "features":[{"type":"Feature","geometry":{"type":"Polygon","coordinates":[ring]},"properties":{"zone_code":"R-3","servicing_type":"serviced","pid":"opcion_2"}},
  {"type":"Feature","geometry":{"type":"Point","coordinates":list(mid)},"properties":{"feature_type":"access","direction":[dx/n,dy/n]}}]}
json.dump(gj,open('run/parcel.geojson','w'),indent=1)
from shapely.geometry import Polygon
pm=Polygon(ring); print('parcel m2',round(pm.area,1),'perimeter',round(pm.length,1))
print('circle radius m',round(R*k,2),'island r',round(Rin*k,2),'circle area in parcel',round(parcel.intersection(circ).area*k*k,1))
# corridor width
def dist(p,a,b):
    (x,y),(x1,y1),(x2,y2)=p,a,b; return abs((x2-x1)*(y1-y)-(x1-x)*(y2-y1))/math.hypot(x2-x1,y2-y1)
print('corridor width m',round(dist(P[13],P[20],P[19])*k,2), round(dist(P[18],P[20],P[19])*k,2))
print('corridor length m', round(math.dist(P[20],P[19])*k,1))
print('edge lengths:'); 
for a,b in zip(order,order[1:]+order[:1]): print(f'  {a}-{b}: {math.dist(P[a],P[b])*k:.2f} m')
print('7 to Nayarit (18.40 label):', round(math.dist((1258,588),(1386,406))*k,2))
json.dump({'k':k,'ox':ox,'oy':oy},open('run/xform.json','w'))
