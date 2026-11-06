from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from .config import settings


def engine_options(database_url: str, serverless: bool = False) -> dict:
    """Build connection options suitable for local and serverless runtimes."""
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    if serverless:
        # Neon supplies a shared pool through its pooled connection URL. A
        # process-local pool would only consume connections across instances.
        return {"poolclass": NullPool}
    return {"pool_pre_ping": True}


engine = create_engine(
    settings.database_url,
    **engine_options(settings.database_url, settings.is_serverless),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

