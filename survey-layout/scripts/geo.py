import json,math
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import split
import numpy as np
P={1:(425,171),2:(612,277),3:(758,365),4:(916,455),12:(855,545),13:(723,761),20:(688,808),21:(617,900),22:(525,1021),23:(472,964),24:(459,939),25:(315,719),26:(182,601),27:(249,487),28:(321,365),
   5:(959,387),6:(1081,469),7:(1258,588),8:(1151,737),10:(1046,670),11:(960,616),14:(864,860),16:(944,911),18:(1001,948),19:(959,1005),'X':(893,1097)}
C=(656.31,652.67); R=145.38; Rin=56.88
order=[1,2,3,4,12,13,20,21,22,23,24,25,26,27,28]
parcel=Polygon([P[i] for i in order])
circ=Point(C).buffer(R,256)
divs=[((708,515),(756,364)),((594,524),(418,184)),((520,611),(231,519)),((530,725),(372,806))]
def lots():
    pieces=[parcel.difference(circ)]
    for a,b in divs:
        a=np.array(a);b=np.array(b);d=b-a; L=LineString([a-d*0.2,b+d*0.2])
        new=[]
        for p in pieces: new+=list(split(p,L).geoms)
        pieces=new
    return sorted([p for p in pieces if p.area>500],key=lambda p:-p.area)
