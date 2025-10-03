from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


class InvalidTokenError(Exception):
    """Raised when a token cannot be decoded."""


def verify_token(token: str) -> dict[str, Any]:
    try:
        return decode_access_token(token)
    except JWTError as exc:  # noqa: B904 - rethrow custom
        raise InvalidTokenError(str(exc)) from exc
