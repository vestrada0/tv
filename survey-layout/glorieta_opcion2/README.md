# Can a vehicle turn around in the Opción 2 circle?

Circle: outer radius 10.22 m (20.4 m across), central island radius 4.0 m. The dashed driving path drawn on the plan is at radius 7.34 m.
The parcel line 12-13 is 7.97 m from the centre, so about 20 m² of the circle lies on the neighbour's lot.
Where the circle meets that line, the space between the island and the parcel edge is only 3.97 m.

Steady turn around the island with 0.30 m clearance:

| Vehicle | Space it needs (from centre) | Fits inside the parcel? |
|---|---|---|
| Car | 4.3–7.1 m | Yes, 0.9 m spare |
| Pickup / SUV | 4.3–7.6 m | Yes, 0.4 m spare |
| Delivery van | 4.3–7.9 m | Just: 0.1 m spare |
| Garbage or fire truck (~8 m) | 4.6–9.6 m | No. It would need the neighbour's ~20 m² and almost the full 20.4 m circle |

Vehicle dimensions are typical, assumed values.

## Driving in from the passage, around the island and back out

Simulated: the vehicle drives in through the 4.1 m passage, goes clockwise round the island (the island is on the driver's right),
then turns left back into the passage. Steering goes from straight to full lock over 1.5 m of travel, and the driver is assumed to be precise.
Turning radii and dimensions are typical, assumed values. The scripts are `sim3.py`, `refine.py` and `drawpath2.py`.

| Vehicle | Minimum clearance, pavement on own land | If the neighbour's ~20 m² were also paved |
|---|---|---|
| Car | 29 cm | 35 cm |
| Pickup / SUV | 1 cm | 11 cm |
| Delivery van | 0 cm, does not fit | 17 cm |
| Garbage or fire truck | does not fit | does not fit |

The tightest point is corner 13, at the passage mouth, where the vehicle swings back into the passage.
The incoming and outgoing paths cross at the passage mouth, so two vehicles cannot use it at the same time.
