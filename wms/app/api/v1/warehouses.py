from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permissions
from app.db.session import get_db
from app.models.org import Warehouse
from app.schemas.common import Paginated
from app.schemas.org import WarehouseCreate, WarehouseRead
from app.utils.pagination import paginate

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@router.get("", response_model=Paginated[WarehouseRead])
def list_warehouses(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    stmt = select(Warehouse)
    if q:
        stmt = stmt.where(Warehouse.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Warehouse.code)
    items, total = paginate(db, stmt, page, size)
    return Paginated[WarehouseRead](
        items=[WarehouseRead.model_validate(item) for item in items], total=total, page=page, size=size
    )


@router.post("", response_model=WarehouseRead, dependencies=[Depends(require_permissions("manage_master"))])
def create_warehouse(
    payload: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Warehouse:
    existing = db.execute(select(Warehouse).where(Warehouse.code == payload.code)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Warehouse code already exists")
    warehouse = Warehouse(**payload.model_dump())
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse
