from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryBalance, InventoryLedger
from app.models.order import SalesOrder


def allocate_sales_order(db: Session, *, sales_order: SalesOrder) -> SalesOrder:
    with db.begin():
        for line in sales_order.lines:
            remaining = line.qty_ordered - line.qty_allocated
            if remaining <= 0:
                continue
            balances = (
                db.execute(
                    select(InventoryBalance)
                    .where(
                        InventoryBalance.sku_id == line.sku_id,
                        InventoryBalance.available > 0,
                    )
                    .order_by(InventoryBalance.available.desc())
                    .with_for_update()
                )
                .scalars()
                .all()
            )
            for balance in balances:
                if remaining <= 0:
                    break
                alloc = min(balance.available, remaining)
                if alloc <= 0:
                    continue
                db.add(
                    InventoryLedger(
                        type="ALLOC",
                        qty=alloc,
                        warehouse_id=balance.warehouse_id,
                        sku_id=balance.sku_id,
                        location_id=balance.location_id,
                        ref_type="SO",
                        ref_id=sales_order.id,
                        ref_no=sales_order.so_no,
                    )
                )
                balance.reserved += alloc
                balance.available = balance.on_hand - balance.reserved
                balance.version += 1
                remaining -= alloc
                line.qty_allocated += alloc
            if remaining > 0:
                raise ValueError("Insufficient inventory for allocation")
        sales_order.status = "ALLOCATED"
        db.flush()
    return sales_order
