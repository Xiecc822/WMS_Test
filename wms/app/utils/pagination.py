from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session


def paginate(db: Session, stmt: Select, page: int = 1, size: int = 20) -> tuple[list[Any], int]:
    page = max(page, 1)
    size = max(min(size, 100), 1)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    results = db.execute(stmt.limit(size).offset((page - 1) * size)).scalars().all()
    return list(results), total
