import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Index, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class MissionStatus(str, enum.Enum):
    planned = "planned"
    active = "active"
    paused = "paused"
    completed = "completed"


class MissionPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


mission_satellites = Table(
    "mission_satellites",
    Base.metadata,
    Column("mission_id", ForeignKey("missions.id", ondelete="CASCADE"), primary_key=True),
    Column("satellite_id", ForeignKey("satellites.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(80))
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    watchlist: Mapped[list["WatchlistItem"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    missions: Mapped[list["Mission"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Satellite(Base):
    __tablename__ = "satellites"
    __table_args__ = (Index("ix_satellite_orbit_name", "orbital_class", "name"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    norad_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    orbital_class: Mapped[str] = mapped_column(String(16), index=True)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    altitude_km: Mapped[float | None] = mapped_column(Float)
    velocity_kps: Mapped[float | None] = mapped_column(Float)
    period_minutes: Mapped[float | None] = mapped_column(Float)
    inclination_deg: Mapped[float | None] = mapped_column(Float)
    data_source: Mapped[str] = mapped_column(String(120), default="CelesTrak reference / demo propagation")
    data_quality: Mapped[str] = mapped_column(String(40), default="demo_estimate")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    watchlisted_by: Mapped[list["WatchlistItem"]] = relationship(back_populates="satellite", cascade="all, delete-orphan")
    missions: Mapped[list["Mission"]] = relationship(secondary=mission_satellites, back_populates="satellites")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (UniqueConstraint("user_id", "satellite_id", name="uq_watchlist_user_satellite"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    satellite_id: Mapped[int] = mapped_column(ForeignKey("satellites.id", ondelete="CASCADE"), index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    notify: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    user: Mapped[User] = relationship(back_populates="watchlist")
    satellite: Mapped[Satellite] = relationship(back_populates="watchlisted_by")


class Mission(Base):
    __tablename__ = "missions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[MissionStatus] = mapped_column(Enum(MissionStatus), default=MissionStatus.planned, index=True)
    priority: Mapped[MissionPriority] = mapped_column(Enum(MissionPriority), default=MissionPriority.medium)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    owner: Mapped[User] = relationship(back_populates="missions")
    satellites: Mapped[list[Satellite]] = relationship(secondary=mission_satellites, back_populates="missions")


class PositionSample(Base):
    __tablename__ = "position_samples"
    __table_args__ = (Index("ix_position_satellite_observed", "satellite_id", "observed_at"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    satellite_id: Mapped[int] = mapped_column(ForeignKey("satellites.id", ondelete="CASCADE"), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    altitude_km: Mapped[float] = mapped_column(Float)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    method: Mapped[str] = mapped_column(String(40), default="propagated_estimate")


class OrbitalElementSnapshot(Base):
    __tablename__ = "orbital_element_snapshots"
    __table_args__ = (
        UniqueConstraint("satellite_id", "tle_line1", "tle_line2", name="uq_satellite_tle"),
        Index("ix_orbital_snapshot_satellite_fetched", "satellite_id", "fetched_at"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    satellite_id: Mapped[int] = mapped_column(ForeignKey("satellites.id", ondelete="CASCADE"), index=True)
    tle_line1: Mapped[str] = mapped_column(String(80))
    tle_line2: Mapped[str] = mapped_column(String(80))
    source_url: Mapped[str] = mapped_column(String(500))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

