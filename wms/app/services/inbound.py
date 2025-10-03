from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Receipt, ReceiptLine
from app.services.inventory import adjust_inventory, move_inventory


def create_receipt(db: Session, *, po_id: int, receipt_no: str) -> Receipt:
    receipt = db.execute(select(Receipt).where(Receipt.receipt_no == receipt_no)).scalar_one_or_none()
    if receipt:
        raise ValueError("Receipt exists")
    receipt = Receipt(po_id=po_id, receipt_no=receipt_no)
    db.add(receipt)
    db.flush()
    return receipt


def receive_line(
    db: Session,
    *,
    receipt_id: int,
    sku_id: int,
    qty_received: int,
    warehouse_id: int,
    staging_location_id: int,
    idempotency_key: str | None = None,
) -> ReceiptLine:
    receipt = db.get(Receipt, receipt_id)
    if receipt is None:
        raise ValueError("Receipt not found")
    line = ReceiptLine(receipt_id=receipt_id, sku_id=sku_id, qty_received=qty_received)
    db.add(line)
    adjust_inventory(
        db,
        warehouse_id=warehouse_id,
        location_id=staging_location_id,
        sku_id=sku_id,
        qty=qty_received,
        reason="RECEIVE",
        ref_no=receipt.receipt_no,
        idempotency_key=idempotency_key,
    )
    receipt.status = "PUTAWAY"
    db.flush()
    return line


def putaway(
    db: Session,
    *,
    receipt_line_id: int,
    to_location_id: int,
    warehouse_id: int,
    staging_location_id: int,
    idempotency_key: str | None = None,
) -> ReceiptLine:
    line = db.get(ReceiptLine, receipt_line_id)
    if line is None:
        raise ValueError("Receipt line not found")
    move_inventory(
        db,
        warehouse_id=warehouse_id,
        sku_id=line.sku_id,
        from_location_id=staging_location_id,
        to_location_id=to_location_id,
        qty=line.qty_received,
        reason="PUTAWAY",
        ref_no=str(line.receipt_id),
        idempotency_key=idempotency_key,
    )
    line.to_location_id = to_location_id
    receipt = db.get(Receipt, line.receipt_id)
    if receipt:
        receipt.status = "CLOSED"
        receipt.received_at = datetime.utcnow()
    db.flush()
    return line
