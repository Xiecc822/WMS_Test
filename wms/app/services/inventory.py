from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryBalance, InventoryLedger


def _get_balance_for_update(
    db: Session, warehouse_id: int, sku_id: int, location_id: int
) -> InventoryBalance:
    stmt: Select[tuple[InventoryBalance]] = (
        select(InventoryBalance)
        .where(
            InventoryBalance.warehouse_id == warehouse_id,
            InventoryBalance.sku_id == sku_id,
            InventoryBalance.location_id == location_id,
        )
        .with_for_update()
    )
    balance = db.execute(stmt).scalar_one_or_none()
    if balance is None:
        balance = InventoryBalance(
            warehouse_id=warehouse_id,
            sku_id=sku_id,
            location_id=location_id,
            on_hand=0,
            reserved=0,
            available=0,
            version=1,
        )
        db.add(balance)
        db.flush()
    return balance


def adjust_inventory(
    db: Session,
    *,
    warehouse_id: int,
    location_id: int,
    sku_id: int,
    qty: int,
    reason: str,
    ref_no: str | None = None,
    idempotency_key: str | None = None,
) -> InventoryBalance:
    with db.begin():
        balance = _get_balance_for_update(db, warehouse_id, sku_id, location_id)
        ledger = InventoryLedger(
            type="ADJ",
            qty=qty,
            warehouse_id=warehouse_id,
            sku_id=sku_id,
            location_id=location_id,
            ref_type=reason,
            ref_no=ref_no,
            idempotency_key=idempotency_key,
        )
        db.add(ledger)
        balance.on_hand += qty
        balance.available = balance.on_hand - balance.reserved
        balance.version += 1
        db.flush()
        return balance


def move_inventory(
    db: Session,
    *,
    warehouse_id: int,
    sku_id: int,
    from_location_id: int,
    to_location_id: int,
    qty: int,
    reason: str,
    ref_no: str | None = None,
    idempotency_key: str | None = None,
) -> tuple[InventoryBalance, InventoryBalance]:
    with db.begin():
        source = _get_balance_for_update(db, warehouse_id, sku_id, from_location_id)
        if source.available < qty:
            raise ValueError("Insufficient inventory to move")
        dest = _get_balance_for_update(db, warehouse_id, sku_id, to_location_id)

        db.add(
            InventoryLedger(
                type="MOVE",
                qty=-qty,
                warehouse_id=warehouse_id,
                sku_id=sku_id,
                location_id=from_location_id,
                ref_type=reason,
                ref_no=ref_no,
                idempotency_key=f"{idempotency_key}-src" if idempotency_key else None,
            )
        )
        db.add(
            InventoryLedger(
                type="MOVE",
                qty=qty,
                warehouse_id=warehouse_id,
                sku_id=sku_id,
                location_id=to_location_id,
                ref_type=reason,
                ref_no=ref_no,
                idempotency_key=f"{idempotency_key}-dst" if idempotency_key else None,
            )
        )

        source.on_hand -= qty
        source.available = source.on_hand - source.reserved
        source.version += 1

        dest.on_hand += qty
        dest.available = dest.on_hand - dest.reserved
        dest.version += 1
        db.flush()
        return source, dest


def get_balance(db: Session, *, warehouse_id: int | None = None, sku_id: int | None = None):
    stmt = select(InventoryBalance)
    if warehouse_id is not None:
        stmt = stmt.where(InventoryBalance.warehouse_id == warehouse_id)
    if sku_id is not None:
        stmt = stmt.where(InventoryBalance.sku_id == sku_id)
    return db.execute(stmt).scalars().all()


def get_ledger(db: Session, *, sku_id: int | None = None, ref_no: str | None = None):
    stmt = select(InventoryLedger)
    if sku_id is not None:
        stmt = stmt.where(InventoryLedger.sku_id == sku_id)
    if ref_no is not None:
        stmt = stmt.where(InventoryLedger.ref_no == ref_no)
    stmt = stmt.order_by(InventoryLedger.ts.desc())
    return db.execute(stmt).scalars().all()
