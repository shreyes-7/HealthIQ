"""Database session management. The connection target is entirely
configurable via `DATABASE_URL` (Backend.app.core.config.Settings) --
nothing here hardcodes a driver or credentials.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from Backend.app.core.config import get_settings


def build_engine(database_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


settings = get_settings()
engine = build_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency: one session per request, always closed
    afterward -- keeps transactions short per CLAUDE.md's database
    guidance."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
