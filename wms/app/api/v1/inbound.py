from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permissions
from app.db.session import get_db
from app.models.order import Receipt, ReceiptLine
from app.services import inbound as inbound_service

router = APIRouter(prefix="/inbound", tags=["inbound"])


@router.post("/receipts", response_model=dict, dependencies=[Depends(require_permissions("receive_inbound"))])
def create_receipt(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> dict:
    try:
        receipt = inbound_service.create_receipt(db, po_id=payload["po_id"], receipt_no=payload["receipt_no"])
        db.commit()
        return {"id": receipt.id, "receipt_no": receipt.receipt_no}
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/receive-line", response_model=dict, dependencies=[Depends(require_permissions("receive_inbound"))])
def receive_line(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> dict:
    try:
        line = inbound_service.receive_line(
            db,
            receipt_id=payload["receipt_id"],
            sku_id=payload["sku_id"],
            qty_received=payload["qty_received"],
            warehouse_id=payload["warehouse_id"],
            staging_location_id=payload["staging_location_id"],
            idempotency_key=payload.get("idempotency_key"),
        )
        db.commit()
        return {"id": line.id, "qty_received": line.qty_received}
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/putaway", response_model=dict, dependencies=[Depends(require_permissions("receive_inbound"))])
def putaway(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> dict:
    try:
        line = inbound_service.putaway(
            db,
            receipt_line_id=payload["receipt_line_id"],
            to_location_id=payload["to_location_id"],
            warehouse_id=payload["warehouse_id"],
            staging_location_id=payload["staging_location_id"],
            idempotency_key=payload.get("idempotency_key"),
        )
        db.commit()
        return {"id": line.id, "to_location_id": line.to_location_id}
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
