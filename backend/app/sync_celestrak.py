"""Opt-in CelesTrak refresh and SGP4 propagation.

Run with ``python -m app.sync_celestrak``. One grouped request is made; results are
cached in PostgreSQL. Propagated positions are estimates, never direct telemetry.
"""
import math
from datetime import datetime, timezone

import httpx
from sgp4.api import Satrec, jday
from sqlalchemy import select

from .database import SessionLocal, engine
from .models import Base, OrbitalElementSnapshot, PositionSample, Satellite
from .seed import seed_satellites

SOURCE_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=TLE"


def parse_tle_catalog(body: str) -> list[tuple[str, str, str]]:
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    records = []
    for index in range(0, len(lines) - 2, 3):
        name, line1, line2 = lines[index:index + 3]
        if line1.startswith("1 ") and line2.startswith("2 "):
            records.append((name, line1, line2))
    return records


def propagate(line1: str, line2: str, observed_at: datetime) -> tuple[float, float, float, float, float, float]:
    sat = Satrec.twoline2rv(line1, line2)
    second = observed_at.second + observed_at.microsecond / 1_000_000
    jd, fraction = jday(observed_at.year, observed_at.month, observed_at.day,
                        observed_at.hour, observed_at.minute, second)
    error, position, velocity = sat.sgp4(jd, fraction)
    if error:
        raise ValueError(f"SGP4 propagation error {error}")
    full_jd = jd + fraction
    centuries = (full_jd - 2451545.0) / 36525.0
    gmst = math.radians((280.46061837 + 360.98564736629 * (full_jd - 2451545.0)
                         + 0.000387933 * centuries ** 2) % 360)
    x, y, z = position
    x_ecef = math.cos(gmst) * x + math.sin(gmst) * y
    y_ecef = -math.sin(gmst) * x + math.cos(gmst) * y
    longitude = math.atan2(y_ecef, x_ecef)
    horizontal = math.hypot(x_ecef, y_ecef)
    semi_major, eccentricity_sq = 6378.137, 6.69437999014e-3
    latitude = math.atan2(z, horizontal * (1 - eccentricity_sq))
    altitude = 0.0
    for _ in range(6):
        normal = semi_major / math.sqrt(1 - eccentricity_sq * math.sin(latitude) ** 2)
        altitude = horizontal / max(math.cos(latitude), 1e-12) - normal
        latitude = math.atan2(z, horizontal * (1 - eccentricity_sq * normal / (normal + altitude)))
    speed = math.sqrt(sum(component * component for component in velocity))
    period = 2 * math.pi / sat.no_kozai
    return math.degrees(latitude), math.degrees(longitude), altitude, speed, period, math.degrees(sat.inclo)


def sync() -> dict[str, int]:
    Base.metadata.create_all(engine)
    with httpx.Client(timeout=20, follow_redirects=True, headers={"User-Agent": "SpaceMissionControl/1.0 portfolio"}) as client:
        response = client.get(SOURCE_URL)
        response.raise_for_status()
    records = parse_tle_catalog(response.text)
    now = datetime.now(timezone.utc)
    updated = skipped = 0
    with SessionLocal() as db:
        seed_satellites(db)
        catalog = {sat.norad_id: sat for sat in db.scalars(select(Satellite)).all()}
        for _name, line1, line2 in records:
            try:
                norad_id = int(line2[2:7])
                satellite = catalog.get(norad_id)
                if not satellite:
                    skipped += 1
                    continue
                latitude, longitude, altitude, speed, period, inclination = propagate(line1, line2, now)
            except (ValueError, IndexError):
                skipped += 1
                continue
            existing = db.scalar(select(OrbitalElementSnapshot).where(
                OrbitalElementSnapshot.satellite_id == satellite.id,
                OrbitalElementSnapshot.tle_line1 == line1,
                OrbitalElementSnapshot.tle_line2 == line2,
            ))
            if not existing:
                db.add(OrbitalElementSnapshot(satellite_id=satellite.id, tle_line1=line1, tle_line2=line2,
                                              source_url=SOURCE_URL, fetched_at=now))
            satellite.latitude, satellite.longitude, satellite.altitude_km = latitude, longitude, altitude
            satellite.velocity_kps, satellite.period_minutes = speed, period
            satellite.inclination_deg, satellite.updated_at = inclination, now
            satellite.data_source, satellite.data_quality = "CelesTrak TLE / SGP4", "tle_propagated_estimate"
            db.add(PositionSample(satellite_id=satellite.id, latitude=latitude, longitude=longitude,
                                  altitude_km=altitude, observed_at=now, method="tle_propagated_estimate"))
            updated += 1
        db.commit()
    return {"received": len(records), "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    print(sync())
