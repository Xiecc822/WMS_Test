import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryBalance, InventoryLedger
from app.models.ops import PickTask, PickTaskLine
from app.models.order import SalesOrder


def generate_tasks(db: Session, *, sales_order: SalesOrder) -> PickTask:
    task_no = f"PICK-{uuid.uuid4().hex[:8]}"
    task = PickTask(so_id=sales_order.id, task_no=task_no)
    db.add(task)
    db.flush()
    for line in sales_order.lines:
        pick_line = PickTaskLine(
            task_id=task.id,
            sku_id=line.sku_id,
            from_location_id=0,
            qty=line.qty_allocated,
        )
        db.add(pick_line)
    sales_order.status = "PICKING"
    db.flush()
    db.refresh(task)
    return task


def confirm_picks(db: Session, *, task: PickTask) -> PickTask:
    with db.begin():
        for line in task.lines:
            balance = db.execute(
                select(InventoryBalance)
                .where(InventoryBalance.sku_id == line.sku_id, InventoryBalance.available + InventoryBalance.reserved > 0)
                .with_for_update()
            ).scalar_one_or_none()
            if balance is None or balance.reserved < line.qty:
                raise ValueError("Insufficient reserved stock")
            db.add(
                InventoryLedger(
                    type="OUT",
                    qty=line.qty,
                    warehouse_id=balance.warehouse_id,
                    sku_id=balance.sku_id,
                    location_id=balance.location_id,
                    ref_type="PICK",
                    ref_id=task.id,
                    ref_no=task.task_no,
                )
            )
            balance.on_hand -= line.qty
            balance.reserved -= line.qty
            balance.available = balance.on_hand - balance.reserved
            balance.version += 1
        task.status = "DONE"
        so = task.sales_order
        if so:
            so.status = "PACKED"
        db.flush()
    return task
