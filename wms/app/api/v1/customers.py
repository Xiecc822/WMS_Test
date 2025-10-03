from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permissions
from app.db.session import get_db
from app.models.org import Customer
from app.schemas.common import Paginated
from app.schemas.org import CustomerCreate, CustomerRead
from app.utils.pagination import paginate

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=Paginated[CustomerRead])
def list_customers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    stmt = select(Customer)
    if q:
        stmt = stmt.where(Customer.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Customer.code)
    items, total = paginate(db, stmt, page, size)
    return Paginated[CustomerRead](
        items=[CustomerRead.model_validate(item) for item in items], total=total, page=page, size=size
    )


@router.post("", response_model=CustomerRead, dependencies=[Depends(require_permissions("manage_master"))])
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Customer:
    existing = db.execute(select(Customer).where(Customer.code == payload.code)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Customer code exists")
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer
