from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permissions
from app.db.session import get_db
from app.models.org import Location
from app.schemas.common import Paginated
from app.schemas.org import LocationCreate, LocationRead
from app.utils.pagination import paginate

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=Paginated[LocationRead])
def list_locations(
    warehouse_id: int | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    stmt = select(Location)
    if warehouse_id:
        stmt = stmt.where(Location.warehouse_id == warehouse_id)
    if q:
        stmt = stmt.where(Location.code.ilike(f"%{q}%"))
    stmt = stmt.order_by(Location.code)
    items, total = paginate(db, stmt, page, size)
    return Paginated[LocationRead](
        items=[LocationRead.model_validate(item) for item in items], total=total, page=page, size=size
    )


@router.post("", response_model=LocationRead, dependencies=[Depends(require_permissions("manage_master"))])
def create_location(
    payload: LocationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Location:
    existing = db.execute(
        select(Location).where(
            and_(Location.warehouse_id == payload.warehouse_id, Location.code == payload.code)
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Location already exists")
    location = Location(**payload.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location
