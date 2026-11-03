from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from .models import MissionPriority, MissionStatus


class UserCreate(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=10, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    display_name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SatelliteOut(BaseModel):
    id: int
    norad_id: int
    name: str
    orbital_class: str
    latitude: float | None
    longitude: float | None
    altitude_km: float | None
    velocity_kps: float | None
    period_minutes: float | None
    inclination_deg: float | None
    data_source: str
    data_quality: str
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SatellitePage(BaseModel):
    items: list[SatelliteOut]
    total: int
    page: int
    page_size: int
    pages: int


class WatchlistCreate(BaseModel):
    satellite_id: int
    notes: str = Field(default="", max_length=2000)
    notify: bool = False


class WatchlistUpdate(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)
    notify: bool | None = None


class WatchlistOut(BaseModel):
    id: int
    satellite: SatelliteOut
    notes: str
    notify: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MissionCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=5000)
    status: MissionStatus = MissionStatus.planned
    priority: MissionPriority = MissionPriority.medium
    satellite_ids: list[int] = Field(default_factory=list, max_length=50)


class MissionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    status: MissionStatus | None = None
    priority: MissionPriority | None = None
    satellite_ids: list[int] | None = Field(default=None, max_length=50)


class MissionOut(BaseModel):
    id: str
    name: str
    description: str
    status: MissionStatus
    priority: MissionPriority
    satellites: list[SatelliteOut]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

