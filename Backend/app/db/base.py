"""The declarative base every SQLAlchemy model inherits from, and the
single import Alembic's env.py needs to autogenerate migrations against
the current set of models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
