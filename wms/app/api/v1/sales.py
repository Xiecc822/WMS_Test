from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permissions
from app.db.session import get_db
from app.models.ops import PickTask, Shipment
from app.models.order import SalesOrder, SalesOrderLine
from app.schemas.ops import PickTaskRead, ShipmentRead
from app.schemas.order import SalesOrderCreate, SalesOrderRead
from app.services import allocation, picking, shipping
from app.tasks.shipping import create_label as create_label_task

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("/orders", response_model=SalesOrderRead, dependencies=[Depends(require_permissions("manage_master"))])
def create_sales_order(
    payload: SalesOrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> SalesOrder:
    existing = db.execute(select(SalesOrder).where(SalesOrder.so_no == payload.so_no)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="SO number exists")
    order = SalesOrder(
        so_no=payload.so_no,
        customer_id=payload.customer_id,
        ship_to_json=payload.ship_to_json,
        carrier_service=payload.carrier_service,
        created_by=current_user.id,
    )
    db.add(order)
    db.flush()
    for line in payload.lines:
        db.add(SalesOrderLine(so_id=order.id, sku_id=line.sku_id, qty_ordered=line.qty_ordered))
    db.commit()
    db.refresh(order, attribute_names=["lines"])
    return order


@router.post("/allocate", response_model=SalesOrderRead, dependencies=[Depends(require_permissions("allocate"))])
def allocate_order(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> SalesOrder:
    order = db.get(SalesOrder, payload["sales_order_id"])
    if order is None:
        raise HTTPException(status_code=404, detail="Sales order not found")
    try:
        allocation.allocate_sales_order(db, sales_order=order)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.refresh(order, attribute_names=["lines"])
    return order


@router.post("/picking/tasks", response_model=PickTaskRead, dependencies=[Depends(require_permissions("pick"))])
def create_pick_task(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> PickTask:
    order = db.get(SalesOrder, payload["sales_order_id"])
    if order is None:
        raise HTTPException(status_code=404, detail="Sales order not found")
    task = picking.generate_tasks(db, sales_order=order)
    db.commit()
    db.refresh(task, attribute_names=["lines"])
    return task


@router.post("/picking/confirm", response_model=PickTaskRead, dependencies=[Depends(require_permissions("pick"))])
def confirm_pick(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> PickTask:
    task = db.get(PickTask, payload["task_id"])
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        picking.confirm_picks(db, task=task)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.refresh(task, attribute_names=["lines"])
    return task


@router.post("/shipping/pack", response_model=ShipmentRead, dependencies=[Depends(require_permissions("ship"))])
def pack_shipment(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Shipment:
    order = db.get(SalesOrder, payload["sales_order_id"])
    if order is None:
        raise HTTPException(status_code=404, detail="Sales order not found")
    shipment = shipping.pack_order(
        db,
        sales_order=order,
        weight_g=payload.get("weight_g"),
        parcels=payload.get("parcels"),
    )
    db.commit()
    db.refresh(shipment)
    return shipment


@router.post("/shipping/label", response_model=ShipmentRead, dependencies=[Depends(require_permissions("ship"))])
def request_label(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Shipment:
    shipment = db.get(Shipment, payload["shipment_id"])
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    try:
        create_label_task.delay(shipment.id)
    except Exception:  # pragma: no cover - fallback when broker unavailable
        shipping.generate_label(db, shipment_id=shipment.id)
    db.commit()
    db.refresh(shipment)
    return shipment


@router.post("/shipping/ship", response_model=ShipmentRead, dependencies=[Depends(require_permissions("ship"))])
def mark_shipment(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Shipment:
    shipment = db.get(Shipment, payload["shipment_id"])
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    shipping.mark_shipped(db, shipment_id=shipment.id, tracking_no=payload.get("tracking_no"))
    db.commit()
    db.refresh(shipment)
    return shipment
