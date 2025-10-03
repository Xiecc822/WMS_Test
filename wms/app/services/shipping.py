import uuid

from sqlalchemy.orm import Session

from app.models.file import FileObject
from app.models.ops import Shipment
from app.models.order import SalesOrder
from app.services import carrier_client
from app.utils import s3


def pack_order(
    db: Session,
    *,
    sales_order: SalesOrder,
    weight_g: int | None,
    parcels: dict | None,
) -> Shipment:
    ship_no = f"SHIP-{uuid.uuid4().hex[:8]}"
    shipment = Shipment(so_id=sales_order.id, ship_no=ship_no, weight_g=weight_g, parcels=parcels)
    db.add(shipment)
    sales_order.status = "PACKED"
    db.flush()
    return shipment


def generate_label(db: Session, *, shipment_id: int) -> Shipment:
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        raise ValueError("Shipment not found")
    provider = carrier_client.get_provider()
    label = provider.create_label(shipment)
    key = f"labels/{uuid.uuid4().hex}.pdf"
    s3.upload_bytes(key, label.label_bytes, "application/pdf")
    file_obj = FileObject(
        key=key,
        bucket=s3.settings.s3_bucket,
        mime="application/pdf",
        size=len(label.label_bytes),
    )
    db.add(file_obj)
    db.flush()
    shipment.label_file_id = file_obj.id
    shipment.status = "LABELED"
    shipment.tracking_no = label.tracking_number
    db.flush()
    return shipment


def mark_shipped(db: Session, *, shipment_id: int, tracking_no: str | None = None) -> Shipment:
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        raise ValueError("Shipment not found")
    shipment.status = "SHIPPED"
    if tracking_no:
        shipment.tracking_no = tracking_no
    order = shipment.sales_order
    if order:
        order.status = "SHIPPED"
    db.flush()
    return shipment
