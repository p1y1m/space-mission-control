import pytest

from app.config import Settings


def test_provider_postgres_urls_use_psycopg_driver():
    standard = Settings(database_url="postgresql://user:password@example.test/app")
    legacy = Settings(database_url="postgres://user:password@example.test/app")

    assert standard.database_url == "postgresql+psycopg://user:password@example.test/app"
    assert legacy.database_url == "postgresql+psycopg://user:password@example.test/app"


def test_explicit_driver_and_sqlite_urls_are_preserved():
    postgres = Settings(database_url="postgresql+psycopg://user:password@example.test/app")
    sqlite = Settings(database_url="sqlite:///./local.db")

    assert postgres.database_url == "postgresql+psycopg://user:password@example.test/app"
    assert sqlite.database_url == "sqlite:///./local.db"


def test_vercel_configuration_requires_secure_production_values():
    with pytest.raises(ValueError, match="Invalid Vercel configuration"):
        Settings(vercel="1")

    configured = Settings(
        vercel="1",
        database_url="postgresql://user:password@example.test/app?sslmode=require",
        secret_key="a-random-production-secret-that-is-long-enough",
        cookie_secure=True,
        cors_origins="https://p1y1m.github.io",
    )
    assert configured.is_serverless is True
    assert configured.database_url.endswith("?sslmode=require")


def test_local_configuration_is_not_serverless():
    assert Settings(vercel=None).is_serverless is False
