import sys, math, numpy as np
sys.path.insert(0,'turn'); sys.path.insert(0,'.')
from sim3 import area, body, VEH, mouth, ax, kmax
from shapely.prepared import prep
nrm=np.array([-ax[1],ax[0]])
rt=-nrm                       # right of travel
C=np.zeros(2)
# frame: origin mouth, y along ax, x to the right
def W(x,y): return mouth+rt*x+ax*y
def path(v,r,re,step=0.1):
    # tangent entry: car travels along x = xc - r (line), circle centre (xc,yc)
    xc=(C-mouth)@rt; yc=(C-mouth)@ax
    x0=xc-r                                  # entry line offset (must be within corridor |x|<2.06-w/2 ideally)
    pts=[]
    # straight from y=-8 to y=yc
    for y in np.arange(-8,yc,step): pts.append((x0,y,math.pi/2))
    # clockwise loop around (xc,yc) from angle pi (left point) going clockwise until heading is -x (bottom point, angle -pi/2)
    for a in np.arange(math.pi, -math.pi/2, -step/r):
        x=xc+r*math.cos(a); y=yc+r*math.sin(a); h=a-math.pi/2   # heading for clockwise
        pts.append((x,y,h))
    # exit: left turn of radius re from bottom point heading -x
    xb,yb=xc,yc-r
    cx,cy=xb,yb-re
    for b in np.arange(0, math.pi/2, step/re):
        x=cx-re*math.sin(b); y=cy+re*math.cos(b); pts.append((x,y,math.pi+b))
    xe,ye=cx-re,cy
    for y in np.arange(ye,ye-8,-step): pts.append((xe,y,-math.pi/2))
    return pts,x0,xe
def run(vname,full):
    v=VEH[vname]; A=area(full); Ap=prep(A); km=kmax(v)
    best=None
    for r in np.arange(1/km,9.0,0.1):
        for re in np.arange(1/km,9.0,0.1):
            pts,x0,xe=path(v,r,re)
            worst=0; 
            for (x,y,h) in pts[::2]:
                # headings: straight up = pi/2 in frame; convert frame heading to world angle
                d=rt*math.cos(h)+ax*math.sin(h); th=math.atan2(d[1],d[0])
                p=W(x,y); b=body(p[0],p[1],th,v)
                if not Ap.contains(b): worst=max(worst,b.difference(A).area)
                if worst>0.5: break
            if best is None or worst<best[0]: best=(worst,r,re,x0,xe)
    return best
if __name__=='__main__':
    for vn in sys.argv[1:]:
        for full in (False,True):
            w,r,re,x0,xe=run(vn,full)
            print(f'{vn:7s} {"full" if full else "own"}: best worst-outside={w:.3f} m2 at loop r={r:.1f} m exit r={re:.1f} m; entry line x={x0:+.2f} exit line x={xe:+.2f} (corridor half-width 2.06)')
def clearance(vname,full,r,re):
    v=VEH[vname]; A=area(full); pts,_,_=path(v,r,re); m=9e9; where=None
    for (x,y,h) in pts[::2]:
        d=rt*math.cos(h)+ax*math.sin(h); th=math.atan2(d[1],d[0]); p=W(x,y); b=body(p[0],p[1],th,v)
        out=b.difference(A).area
        c=-out if out>1e-6 else A.boundary.distance(b)
        if c<m: m=c; where=(round(x,1),round(y,1))
    return m,where
