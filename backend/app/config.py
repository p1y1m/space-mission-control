from functools import lru_cache
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Space Mission Control API"
    environment: str = "development"
    database_url: str = "sqlite:///./mission_control.db"
    secret_key: str = "development-only-secret-key-change-me"
    cors_origins: str = "http://localhost:5173"
    cookie_secure: bool = False
    token_minutes: int = 720
    vercel: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        """Accept provider PostgreSQL URLs while consistently using psycopg 3."""
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value.removeprefix("postgres://")
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value.removeprefix("postgresql://")
        return value

    @model_validator(mode="after")
    def reject_insecure_serverless_configuration(self):
        """Fail closed instead of silently deploying development defaults."""
        if not self.vercel:
            return self
        problems = []
        if self.database_url.startswith("sqlite"):
            problems.append("DATABASE_URL must be a Neon PostgreSQL URL")
        if len(self.secret_key) < 32 or self.secret_key in {
            "development-only-secret-key-change-me",
            "replace-with-at-least-32-random-characters",
        }:
            problems.append("SECRET_KEY must contain at least 32 random characters")
        if not self.cookie_secure:
            problems.append("COOKIE_SECURE must be true")
        if not self.origins or any(not origin.startswith("https://") for origin in self.origins):
            problems.append("CORS_ORIGINS must contain only HTTPS origins")
        if problems:
            raise ValueError("Invalid Vercel configuration: " + "; ".join(problems))
        return self

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_serverless(self) -> bool:
        """Return whether the app is running in Vercel's serverless runtime."""
        return bool(self.vercel)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

