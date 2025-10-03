from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permissions
from app.db.session import get_db
from app.models.rbac import Permission, Role
from app.schemas.rbac import PermissionCreate, PermissionRead, RoleCreate, RoleRead

router = APIRouter(prefix="/roles", tags=["rbac"])


@router.get("", response_model=list[RoleRead], dependencies=[Depends(require_permissions("view_roles"))])
def list_roles(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)) -> list[Role]:
    roles = db.execute(select(Role).order_by(Role.name)).scalars().all()
    return roles


@router.post("", response_model=RoleRead, dependencies=[Depends(require_permissions("manage_roles"))])
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Role:
    existing = db.execute(select(Role).where(Role.name == payload.name)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Role name exists")
    permissions = []
    if payload.permission_ids:
        permissions = db.execute(
            select(Permission).where(Permission.id.in_(payload.permission_ids))
        ).scalars().all()
    role = Role(name=payload.name, description=payload.description, permissions=permissions)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


permissions_router = APIRouter(prefix="/permissions", tags=["rbac"])


@permissions_router.get("", response_model=list[PermissionRead], dependencies=[Depends(require_permissions("view_roles"))])
def list_permissions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> list[Permission]:
    return db.execute(select(Permission).order_by(Permission.code)).scalars().all()


@permissions_router.post("", response_model=PermissionRead, dependencies=[Depends(require_permissions("manage_roles"))])
def create_permission(
    payload: PermissionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Permission:
    existing = db.execute(select(Permission).where(Permission.code == payload.code)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Permission code exists")
    perm = Permission(code=payload.code, description=payload.description)
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm
