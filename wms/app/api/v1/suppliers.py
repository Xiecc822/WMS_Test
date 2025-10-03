from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permissions
from app.db.session import get_db
from app.models.org import Supplier
from app.schemas.common import Paginated
from app.schemas.org import SupplierCreate, SupplierRead
from app.utils.pagination import paginate

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=Paginated[SupplierRead])
def list_suppliers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    stmt = select(Supplier)
    if q:
        stmt = stmt.where(Supplier.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Supplier.code)
    items, total = paginate(db, stmt, page, size)
    return Paginated[SupplierRead](
        items=[SupplierRead.model_validate(item) for item in items], total=total, page=page, size=size
    )


@router.post("", response_model=SupplierRead, dependencies=[Depends(require_permissions("manage_master"))])
def create_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Supplier:
    existing = db.execute(select(Supplier).where(Supplier.code == payload.code)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Supplier code exists")
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier
