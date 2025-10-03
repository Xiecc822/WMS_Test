from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from sqlalchemy.orm import Session

from app.models.log import OperationLog
from app.models.user import User


def _serialize_state(state: Any) -> Any:
    if state is None:
        return None
    if hasattr(state, "model_dump"):
        return state.model_dump()
    if hasattr(state, "__dict__"):
        return {
            key: value
            for key, value in state.__dict__.items()
            if not key.startswith("_")
        }
    return state


def audit_operation(action: str, entity: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            db: Session | None = kwargs.get("db")
            current_user: User | None = kwargs.get("current_user")
            before_state = _serialize_state(kwargs.get("before_state"))
            result = func(*args, **kwargs)
            after_state = _serialize_state(kwargs.get("after_state") or result)

            if db is not None and current_user is not None:
                log = OperationLog(
                    user_id=current_user.id,
                    action=action,
                    entity=entity,
                    entity_id=getattr(result, "id", None),
                    before_json=before_state,
                    after_json=after_state,
                )
                db.add(log)
                db.flush()
            return result

        return wrapper

    return decorator
