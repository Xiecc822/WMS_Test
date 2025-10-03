from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permissions
from app.db.session import get_db
from app.models.product import SKU
from app.schemas.common import Paginated
from app.schemas.product import SKUCreate, SKURead
from app.utils.pagination import paginate

router = APIRouter(prefix="/skus", tags=["skus"])


@router.get("", response_model=Paginated[SKURead])
def list_skus(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    stmt = select(SKU)
    if q:
        stmt = stmt.where(SKU.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(SKU.code)
    items, total = paginate(db, stmt, page, size)
    return Paginated[SKURead](items=[SKURead.model_validate(item) for item in items], total=total, page=page, size=size)


@router.post("", response_model=SKURead, dependencies=[Depends(require_permissions("manage_master"))])
def create_sku(
    payload: SKUCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> SKU:
    existing = db.execute(select(SKU).where(SKU.code == payload.code)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="SKU code exists")
    sku = SKU(**payload.model_dump())
    db.add(sku)
    db.commit()
    db.refresh(sku)
    return sku
