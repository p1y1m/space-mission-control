import json
import logging
import math
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import String, cast, func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .config import settings
from .database import SessionLocal, engine, get_db
from .models import Base, Mission, Satellite, User, WatchlistItem
from .schemas import (LoginRequest, MissionCreate, MissionOut, MissionUpdate, SatelliteOut,
                      SatellitePage, UserCreate, UserOut, WatchlistCreate, WatchlistOut, WatchlistUpdate)
from .security import create_token, current_user, hash_password, new_csrf_token, verify_password
from .seed import seed_satellites


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "level": record.levelname,
                           "logger": record.name, "message": record.getMessage()})


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("mission_control")
logger.handlers = [handler]
logger.setLevel(logging.INFO)
attempts: dict[str, deque[float]] = defaultdict(deque)


def rate_limit(request: Request):
    key = request.client.host if request.client else "unknown"
    now = time.monotonic()
    bucket = attempts[key]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= 12:
        raise HTTPException(429, "Too many authentication attempts; try again shortly")
    bucket.append(now)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Local development remains zero-setup. Vercel runs migrations and seeding
    # once during its build instead of on every serverless cold start.
    if not settings.is_serverless:
        Base.metadata.create_all(engine)
        with SessionLocal() as db:
            seed_satellites(db)
    logger.info("application_started serverless=%s", settings.is_serverless)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan,
              description="Satellite catalog, private watchlists, and simulated mission planning API.")
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True,
                   allow_methods=["GET", "POST", "PATCH", "DELETE"],
                   allow_headers=["Content-Type", "X-CSRF-Token"],
                   expose_headers=["X-CSRF-Token"])


@app.middleware("http")
async def security_and_logging(request: Request, call_next):
    started = time.perf_counter()
    if request.method in {"POST", "PATCH", "PUT", "DELETE"} and request.cookies.get("smc_session"):
        csrf_cookie = request.cookies.get("smc_csrf")
        if not csrf_cookie or request.headers.get("X-CSRF-Token") != csrf_cookie:
            return Response(content=json.dumps({"detail": "CSRF validation failed"}), status_code=403,
                            media_type="application/json")
    response = await call_next(request)
    csrf_cookie = request.cookies.get("smc_csrf")
    if csrf_cookie and "X-CSRF-Token" not in response.headers:
        # The GitHub Pages origin cannot read a cookie scoped to vercel.app.
        # CORS exposes this response header only to explicitly allowed origins.
        response.headers["X-CSRF-Token"] = csrf_cookie
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    logger.info(json.dumps({"method": request.method, "path": request.url.path, "status": response.status_code,
                            "duration_ms": round((time.perf_counter() - started) * 1000, 2)}))
    return response


@app.get("/", include_in_schema=False)
def root():
    """Provide an unambiguous deployment probe at the project root."""
    return {
        "service": "space-mission-control-api",
        "status": "ok",
        "health": "/health",
        "docs": "/docs",
    }


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        database = "connected"
    except Exception:
        database = "unavailable"
    return {"status": "ok" if database == "connected" else "degraded", "database": database,
            "service": "space-mission-control-api", "timestamp": datetime.now(timezone.utc)}


def set_session(response: Response, user_id: str):
    same_site = "none" if settings.cookie_secure else "lax"
    csrf_token = new_csrf_token()
    response.set_cookie("smc_session", create_token(user_id), httponly=True, secure=settings.cookie_secure,
                        samesite=same_site, max_age=settings.token_minutes * 60, path="/")
    response.set_cookie("smc_csrf", csrf_token, httponly=False, secure=settings.cookie_secure,
                        samesite=same_site, max_age=settings.token_minutes * 60, path="/")
    response.headers["X-CSRF-Token"] = csrf_token


@app.post("/api/v1/auth/register", response_model=UserOut, status_code=201, dependencies=[Depends(rate_limit)])
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists")
    user = User(email=email, display_name=payload.display_name.strip(), password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    set_session(response, user.id)
    return user


@app.post("/api/v1/auth/login", response_model=UserOut, dependencies=[Depends(rate_limit)])
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    set_session(response, user.id)
    return user


@app.post("/api/v1/auth/logout", status_code=204)
def logout(response: Response):
    same_site = "none" if settings.cookie_secure else "lax"
    # Match the attributes used when setting the cookies. This is required by
    # cross-site browser policies and prevents a stale secure session from
    # surviving logout on the GitHub Pages frontend.
    response.delete_cookie("smc_session", path="/", httponly=True,
                           secure=settings.cookie_secure, samesite=same_site)
    response.delete_cookie("smc_csrf", path="/", httponly=False,
                           secure=settings.cookie_secure, samesite=same_site)
    response.headers["X-CSRF-Token"] = ""


@app.get("/api/v1/auth/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user


@app.get("/api/v1/satellites", response_model=SatellitePage)
def satellites(search: str = Query("", max_length=100), orbit: str | None = Query(None, pattern="^(LEO|MEO|GEO)$"),
               sort: str = Query("name", pattern="^(name|altitude|updated)$"), page: int = Query(1, ge=1),
               page_size: int = Query(12, ge=1, le=50), db: Session = Depends(get_db)):
    query, count_query = select(Satellite), select(func.count()).select_from(Satellite)
    if search:
        condition = or_(Satellite.name.ilike(f"%{search}%"), cast(Satellite.norad_id, String).ilike(f"%{search}%"))
        query, count_query = query.where(condition), count_query.where(condition)
    if orbit:
        query, count_query = query.where(Satellite.orbital_class == orbit), count_query.where(Satellite.orbital_class == orbit)
    order = {"name": Satellite.name, "altitude": Satellite.altitude_km.desc(), "updated": Satellite.updated_at.desc()}[sort]
    total = db.scalar(count_query) or 0
    items = db.scalars(query.order_by(order).offset((page - 1) * page_size).limit(page_size)).all()
    return SatellitePage(items=items, total=total, page=page, page_size=page_size,
                         pages=max(1, math.ceil(total / page_size)))


@app.get("/api/v1/satellites/{satellite_id}", response_model=SatelliteOut)
def satellite_detail(satellite_id: int, db: Session = Depends(get_db)):
    item = db.get(Satellite, satellite_id)
    if not item:
        raise HTTPException(404, "Satellite not found")
    return item


@app.get("/api/v1/watchlist", response_model=list[WatchlistOut])
def watchlist(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(WatchlistItem).options(selectinload(WatchlistItem.satellite))
                      .where(WatchlistItem.user_id == user.id).order_by(WatchlistItem.created_at.desc())).all()


@app.post("/api/v1/watchlist", response_model=WatchlistOut, status_code=201)
def add_watchlist(payload: WatchlistCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not db.get(Satellite, payload.satellite_id):
        raise HTTPException(404, "Satellite not found")
    item = WatchlistItem(user_id=user.id, **payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Satellite is already in your watchlist")
    return db.scalar(select(WatchlistItem).options(selectinload(WatchlistItem.satellite)).where(WatchlistItem.id == item.id))


def owned_watchlist(item_id: int, user: User, db: Session):
    item = db.scalar(select(WatchlistItem).options(selectinload(WatchlistItem.satellite))
                     .where(WatchlistItem.id == item_id, WatchlistItem.user_id == user.id))
    if not item:
        raise HTTPException(404, "Watchlist item not found")
    return item


@app.patch("/api/v1/watchlist/{item_id}", response_model=WatchlistOut)
def update_watchlist(item_id: int, payload: WatchlistUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = owned_watchlist(item_id, user, db)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit(); db.refresh(item)
    return item


@app.delete("/api/v1/watchlist/{item_id}", status_code=204)
def delete_watchlist(item_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = owned_watchlist(item_id, user, db)
    db.delete(item); db.commit()


def mission_query(user_id: str):
    return select(Mission).options(selectinload(Mission.satellites)).where(Mission.owner_id == user_id)


@app.get("/api/v1/missions", response_model=list[MissionOut])
def missions(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(mission_query(user.id).order_by(Mission.updated_at.desc())).all()


def attach_satellites(db: Session, ids: list[int]):
    satellites = list(db.scalars(select(Satellite).where(Satellite.id.in_(set(ids)))).all()) if ids else []
    if len(satellites) != len(set(ids)):
        raise HTTPException(422, "One or more satellites do not exist")
    return satellites


@app.post("/api/v1/missions", response_model=MissionOut, status_code=201)
def create_mission(payload: MissionCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    mission = Mission(owner_id=user.id, **payload.model_dump(exclude={"satellite_ids"}),
                      satellites=attach_satellites(db, payload.satellite_ids))
    db.add(mission); db.commit()
    return db.scalar(mission_query(user.id).where(Mission.id == mission.id))


def owned_mission(mission_id: str, user: User, db: Session):
    mission = db.scalar(mission_query(user.id).where(Mission.id == mission_id))
    if not mission:
        raise HTTPException(404, "Mission not found")
    return mission


@app.patch("/api/v1/missions/{mission_id}", response_model=MissionOut)
def update_mission(mission_id: str, payload: MissionUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    mission = owned_mission(mission_id, user, db)
    values = payload.model_dump(exclude_unset=True)
    ids = values.pop("satellite_ids", None)
    for key, value in values.items():
        setattr(mission, key, value)
    if ids is not None:
        mission.satellites = attach_satellites(db, ids)
    db.commit()
    return db.scalar(mission_query(user.id).where(Mission.id == mission.id))


@app.delete("/api/v1/missions/{mission_id}", status_code=204)
def delete_mission(mission_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    mission = owned_mission(mission_id, user, db)
    db.delete(mission); db.commit()


@app.get("/api/v1/analytics")
def analytics(user: User = Depends(current_user), db: Session = Depends(get_db)):
    orbit = dict(db.execute(select(Satellite.orbital_class, func.count()).group_by(Satellite.orbital_class)).all())
    mission_status = dict(db.execute(select(Mission.status, func.count()).where(Mission.owner_id == user.id)
                                     .group_by(Mission.status)).all())
    watch_orbit = dict(db.execute(select(Satellite.orbital_class, func.count()).join(WatchlistItem)
                                  .where(WatchlistItem.user_id == user.id).group_by(Satellite.orbital_class)).all())
    avg_altitude = db.scalar(select(func.avg(Satellite.altitude_km))) or 0
    return {"satellites_by_orbit": orbit, "mission_status": {k.value: v for k, v in mission_status.items()},
            "watchlist_by_orbit": watch_orbit, "average_altitude_km": round(avg_altitude, 1),
            "tracked_satellites": sum(orbit.values()), "generated_at": datetime.now(timezone.utc)}
