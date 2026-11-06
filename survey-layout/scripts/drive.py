import sys, json, os, io, contextlib
REPO=sys.argv[1]; OUT=sys.argv[2]; sys.path.insert(0,REPO)
from intake_geojson import load_geojson_parcel
from models import LayoutRules, RoadPattern
from generator import LayoutGenerator
from checker import LotChecker, LayoutScorer
from export import export_geojson, export_dxf
SCEN={
 'A_lot120_road6': dict(min_lot_area=120,min_frontage=7,min_depth=12,min_width=7,row_width=6,carriageway_width=6,cul_de_sac_bulb_radius=6,lot_width_target=8,lot_depth_target=16),
 'B_lot160_road8': dict(min_lot_area=160,min_frontage=8,min_depth=14,min_width=8,row_width=8,carriageway_width=7,cul_de_sac_bulb_radius=8,lot_width_target=10,lot_depth_target=17),
}
COMMON=dict(min_buildable_envelope=50,front_setback=2,rear_setback=3,side_setback=0,flankage_setback=0,sidewalk_required=False,
            max_density=None,max_lot_coverage=0.7,private_road_min_width=6,open_space_dedication_pct=0.0,cul_de_sac_max_length=80)
summary=[]
for sname,s in SCEN.items():
  for pat in list(RoadPattern):
    parcel=load_geojson_parcel(sys.argv[3])
    rules=LayoutRules(**{**COMMON,**s})
    try:
        buf=io.StringIO()
        with contextlib.redirect_stdout(buf):
            gen=LayoutGenerator(parcel,rules); r=gen.generate_layout(pat)
            LotChecker(rules,parcel.constraint_areas).check_layout(r); LayoutScorer(rules).score_layout(r)
    except Exception as e:
        summary.append(dict(scen=sname,pattern=pat.value,error=f'{type(e).__name__}: {e}'[:160])); continue
    lots=[l for l in r.lots]
    ok=lambda l:l.passes_all
    row=dict(scen=sname,pattern=pat.value,shape=str(parcel.shape),n_lots=len(lots),
        
        passing=sum(1 for l in lots if ok(l)),
        road_area=round(r.road_area,1), remainder=round(r.remainder_area,1), passing_area=round(r.passing_lot_area,1),
        lot_detail=[dict(id=l.id,type=l.lot_type.value,area=round(l.area,1),front=round(l.frontage,1),depth=round(l.depth,1),ok=l.passes_all,why=[k for k in ('area','frontage','depth','shape','buildable','access') if not getattr(l,'passes_'+k)]) for l in lots],
        score=round(r.score.total_score,2) if r.score else None)
    summary.append(row)
    p=f'{OUT}/{sname}_{pat.value}'
    with contextlib.redirect_stdout(io.StringIO()):
        export_geojson(r,p+'.geojson'); export_dxf(r,p+'.dxf')
json.dump(summary,open(f'{OUT}/summary.json','w'),indent=1)
for row in summary: print(row)
