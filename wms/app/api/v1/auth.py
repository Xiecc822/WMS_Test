from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models.log import LoginLog
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth import authenticate_user, create_user_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    user: User | None = None
    success = False
    token = ""
    try:
        user = authenticate_user(db, data.email, data.password)
        token = create_user_token(user)
        success = True
        return TokenResponse(access_token=token)
    except Exception:
        db.rollback()
        raise
    finally:
        log = LoginLog(
            user_id=user.id if user else None,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=success,
        )
        db.add(log)
        db.commit()


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user
