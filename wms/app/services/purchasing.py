from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import PurchaseOrder, PurchaseOrderLine


def create_purchase_order(
    db: Session,
    *,
    po_no: str,
    supplier_id: int,
    created_by: int | None,
    lines: list[dict[str, int]],
) -> PurchaseOrder:
    existing = db.execute(select(PurchaseOrder).where(PurchaseOrder.po_no == po_no)).scalar_one_or_none()
    if existing:
        raise ValueError("PO number exists")
    po = PurchaseOrder(po_no=po_no, supplier_id=supplier_id, created_by=created_by)
    db.add(po)
    db.flush()
    for line in lines:
        pol = PurchaseOrderLine(po_id=po.id, sku_id=line["sku_id"], qty_ordered=line["qty_ordered"])
        db.add(pol)
    db.flush()
    db.refresh(po)
    return po
