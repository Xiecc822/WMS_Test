from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models for Alembic metadata
try:
    from app.db import init as _models  # noqa: F401
except Exception:  # pragma: no cover - best effort during app init
    _models = None
