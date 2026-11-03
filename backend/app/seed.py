from datetime import datetime, timezone
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .models import Satellite

# A deliberately bounded catalog. Positions are illustrative propagated estimates;
# NORAD IDs identify real spacecraft, but these coordinates are not telemetry.
SATELLITES = [
    (25544, "ISS (ZARYA)", "LEO", 18.21, -32.44, 419.2, 7.66, 92.9, 51.64),
    (20580, "HUBBLE SPACE TELESCOPE", "LEO", -12.84, 91.27, 536.8, 7.59, 95.4, 28.47),
    (43013, "NOAA 20", "LEO", 48.18, -121.70, 824.0, 7.45, 101.4, 98.72),
    (39084, "LANDSAT 8", "LEO", -43.50, 16.20, 705.0, 7.50, 98.9, 98.21),
    (49260, "LANDSAT 9", "LEO", 62.14, 42.85, 705.0, 7.50, 98.9, 98.22),
    (33591, "NOAA 19", "LEO", 7.40, 144.20, 850.0, 7.42, 102.1, 99.19),
    (41866, "GOES 16", "GEO", 0.02, -75.20, 35786.0, 3.07, 1436.1, 0.04),
    (43226, "GOES 17", "GEO", -0.04, -137.20, 35786.0, 3.07, 1436.1, 0.05),
    (51850, "GOES 18", "GEO", 0.01, -137.00, 35786.0, 3.07, 1436.1, 0.03),
    (25994, "TERRA", "LEO", 36.22, 64.91, 705.0, 7.50, 98.9, 98.21),
    (27424, "AQUA", "LEO", -55.10, -7.42, 705.0, 7.50, 98.8, 98.20),
    (36508, "CRYOSAT 2", "LEO", 70.14, -16.78, 717.0, 7.49, 99.2, 92.03),
    (40697, "SENTINEL-2A", "LEO", 28.31, 128.17, 786.0, 7.46, 100.6, 98.57),
    (42063, "SENTINEL-2B", "LEO", -30.22, -51.78, 786.0, 7.46, 100.6, 98.57),
    (37849, "GALILEO-FM2", "MEO", 31.77, 10.35, 23222.0, 3.88, 845.0, 56.0),
    (28474, "GPS BIIR-13", "MEO", -18.20, 72.22, 20200.0, 3.87, 718.0, 55.0),
]


def seed_satellites(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(Satellite)):
        return
    now = datetime.now(timezone.utc)
    for idx, row in enumerate(SATELLITES, start=1):
        norad, name, orbit, lat, lon, alt, vel, period, inc = row
        db.add(Satellite(id=idx, norad_id=norad, name=name, orbital_class=orbit,
                         latitude=lat, longitude=lon, altitude_km=alt, velocity_kps=vel,
                         period_minutes=period, inclination_deg=inc,
                         data_source="CelesTrak catalog reference; bundled demo propagation",
                         data_quality="demo_propagated_estimate", updated_at=now))
    db.commit()
