"""One-time database preparation invoked by the Vercel build."""

from alembic import command
from alembic.config import Config

from .database import SessionLocal
from .seed import seed_satellites


def main() -> None:
    command.upgrade(Config("alembic.ini"), "head")
    with SessionLocal() as db:
        seed_satellites(db)


if __name__ == "__main__":
    main()
