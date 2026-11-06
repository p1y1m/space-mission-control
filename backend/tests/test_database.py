from sqlalchemy.pool import NullPool

from app.database import engine_options


def test_serverless_postgres_uses_no_process_local_pool():
    options = engine_options("postgresql+psycopg://example.test/app", serverless=True)
    assert options == {"poolclass": NullPool}


def test_local_database_connection_options():
    assert engine_options("postgresql+psycopg://example.test/app") == {"pool_pre_ping": True}
    assert engine_options("sqlite:///./app.db") == {
        "connect_args": {"check_same_thread": False}
    }
