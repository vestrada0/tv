import json, math, sys, numpy as np
sys.path.insert(0,'.')
from geo import P, C, R, Rin, parcel
k=0.07032598126928438
segs=json.load(open('segs.json'))
rs=[math.dist(p,C)*k for w,a,b in segs for p in (a,b) if 6.5<math.dist(p,C)*k<8.0]
print('dashed path radius: median %.2f m (n=%d)'%(np.median(rs),len(rs)))
def dist(p,a,b):
    (x,y),(x1,y1),(x2,y2)=p,a,b; return abs((x2-x1)*(y1-y)-(x1-x)*(y2-y1))/math.hypot(x2-x1,y2-y1)
clip=dist(C,P[12],P[13])*k
island=Rin*k; outer=R*k
# vehicles: wheelbase, width, front overhang, rear overhang, track, min kerb turning radius (outer front wheel)
V={'car (sedan)':(2.70,1.80,0.90,1.00,1.55,5.5),
   'pickup / SUV':(3.30,1.95,0.95,1.30,1.65,6.3),
   'delivery van':(3.67,2.02,1.00,1.20,1.73,6.5),
   'garbage / fire truck (~8 m)':(5.00,2.50,1.50,1.50,2.10,8.5)}
print(f'island r={island:.2f}  outer r={outer:.2f}  property line at {clip:.2f} m from centre (ring there {clip-island:.2f} m wide)')
for n,(wb,w,fo,ro,tr,rmin) in V.items():
    Rr=island+0.30+w/2          # hug the island with 30 cm clearance
    out=math.hypot(Rr+w/2,wb+fo)
    wheel=math.hypot(Rr+tr/2,wb)
    ok_steer=wheel>=rmin
    # tightest possible circle for this vehicle (no island), outer body radius
    Rr_min=math.sqrt(rmin**2-wb**2)-tr/2; out_min=math.hypot(Rr_min+w/2,wb+fo)
    print(f'{n:30s} around island: needs r {island+0.3:.1f}–{out:.2f} m  steer ok={ok_steer}  '
          f'fits full circle: {out<=outer}  fits clipped side: {out<=clip} (margin {clip-out:+.2f} m) | '
          f'U-turn w/o island needs circle diameter {2*out_min:.1f} m')
