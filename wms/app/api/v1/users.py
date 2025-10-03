from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permissions
from app.db.session import get_db
from app.models.rbac import Role
from app.models.user import User
from app.schemas.common import Paginated
from app.schemas.user import UserCreate, UserRead
from app.utils.hashing import get_password_hash
from app.utils.pagination import paginate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=Paginated[UserRead], dependencies=[Depends(require_permissions("view_users"))])
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    stmt = select(User)
    if q:
        stmt = stmt.where(User.full_name.ilike(f"%{q}%"))
    stmt = stmt.order_by(User.created_at.desc())
    items, total = paginate(db, stmt, page, size)
    return Paginated[UserRead](items=[UserRead.model_validate(item) for item in items], total=total, page=page, size=size)


@router.post("", response_model=UserRead, dependencies=[Depends(require_permissions("manage_users"))])
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> User:
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        dept_id=payload.dept_id,
        is_active=payload.is_active,
        password_hash=get_password_hash(payload.password),
    )
    if payload.role_ids:
        roles = db.execute(select(Role).where(Role.id.in_(payload.role_ids))).scalars().all()
        user.roles = list(roles)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
