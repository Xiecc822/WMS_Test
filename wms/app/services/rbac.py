from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rbac import Permission, Role


def list_permissions(db: Session) -> Sequence[Permission]:
    return db.execute(select(Permission).order_by(Permission.code)).scalars().all()


def create_permission(db: Session, code: str, description: str | None = None) -> Permission:
    perm = Permission(code=code, description=description)
    db.add(perm)
    db.flush()
    return perm


def list_roles(db: Session) -> Sequence[Role]:
    return db.execute(select(Role).order_by(Role.name)).scalars().all()


def create_role(db: Session, name: str, description: str | None, permission_ids: Iterable[int]) -> Role:
    permissions = (
        db.execute(select(Permission).where(Permission.id.in_(list(permission_ids)))).scalars().all()
    )
    role = Role(name=name, description=description, permissions=list(permissions))
    db.add(role)
    db.flush()
    return role
