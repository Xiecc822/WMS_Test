from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permissions
from app.db.session import get_db
from app.models.order import PurchaseOrder
from app.schemas.order import PurchaseOrderCreate, PurchaseOrderRead
from app.services.purchasing import create_purchase_order

router = APIRouter(prefix="/purchase-orders", tags=["purchase"])


@router.post("", response_model=PurchaseOrderRead, dependencies=[Depends(require_permissions("create_po"))])
def create_po(
    payload: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> PurchaseOrder:
    try:
        po = create_purchase_order(
            db,
            po_no=payload.po_no,
            supplier_id=payload.supplier_id,
            created_by=current_user.id,
            lines=[line.model_dump() for line in payload.lines],
        )
        db.commit()
        db.refresh(po, attribute_names=["lines"])
        return po
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
