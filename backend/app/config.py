from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Space Mission Control API"
    environment: str = "development"
    database_url: str = "sqlite:///./mission_control.db"
    secret_key: str = "development-only-secret-key-change-me"
    cors_origins: str = "http://localhost:5173"
    cookie_secure: bool = False
    token_minutes: int = 720
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

