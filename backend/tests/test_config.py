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
