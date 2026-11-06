# Opción 2: lot layout test with subdivision-agent

Concept test only. Not a survey and not a legal subdivision plan.

## Inputs
- `opcion_2_parcel_local_m.geojson`: parcel boundary (points 1-2-3-4-12-13-20-21-22-23-24-25-26-27-28),
  extracted from the vector linework of `opcion_2.pdf`. Coordinates are local metres with point 26 at the origin.
  The CRS tag says EPSG:2961 only because the tool accepts nothing else; no reprojection is applied.
- Scale was calibrated against the five labelled lot areas: 0.0703 m per px at 150 dpi.
  Four lots match within 2% and the smallest within 3%.
  The "18.40 Mts." label near point 7 measures about 15.6 m at this scale, so that label is not consistent with the lot areas.
- Access: midpoint of edge 13-20, the mouth of the 4.1–5.0 m corridor to Calle Libertad.

## Rule sets (assumed placeholders, not the real municipal rules)
| | A | B |
|---|---|---|
| Min lot area | 120 m² | 160 m² |
| Min frontage | 7 m | 8 m |
| Road right-of-way | 6 m | 8 m |
| Setbacks | front 2 m, rear 3 m, side 0 m | same |

## Results
| Layout | Lots | Lots passing | Lot area | Road | Unusable |
|---|---|---|---|---|---|
| Current Opción 2 (circular turnaround) | 5 | 5 under A; 4 under B (130.58 m² lot) | 1,254 m² | 308 m² | 0 |
| Tool, rules A (straight lane) | 8 | 6 (2 others at 113 and 120 m²) | 1,016 m² | 240 m² | 269 m² leftover with no access, plus 53 m² unassigned |
| Tool, rules B | 6 | 1 | 910 m² | 320 m² | 188 m² leftover |

## Tool caveats
- The repo's `main.py` ignores `--geojson`, so `scripts/drive.py` calls the engine directly.
- For irregular parcels every road pattern (cul-de-sac, loop, T, cluster) gives the same single-lane layout.
- The "existing_road" pattern assumes a street along the whole front edge, which this parcel does not have, so ignore it.
- The road extends about 12 m² past the boundary.
- subdivision-agent has no license; it was run locally and none of its code is included here.

## Raúl Ruiz de Haro project (straight 4 m lane)
Extracted from `Raúl_Ruiz_de_Haro_Proyecto.pdf` (see `scripts/geo2.py`). The printed dimensions match the drawing
to within 0.02 m, and all six lot areas to within 0.2 m².

| | Opción 2 | Ruiz de Haro project |
|---|---|---|
| Parcel | ~1,567 m² (estimated from lot areas) | 1,569.8 m² (from dimensions) |
| Lots | 5 (131–376 m²) | 6 (232.00–238.00 m²) |
| Saleable | 1,254 m² (80%) | 1,414.66 m² (90%) |
| Road | ~308 m² circle | 155 m² lane, 4.0 m wide × 38.6 m |

Open issues with the project:
- The lane is 4.0 m wide and dead-ends about 62 m from Calle Libertad (38.6 m lane plus the 23.6 m passage), with no place to turn around.
- One tree stands in the lane at its west end. Another is 0.6 m from the lane at the east entrance, in the 235.58 m² lot.
- The "18.40 Mts." label near point 7 measures 15.6 m in this drawing as well. It is outside the parcel.
