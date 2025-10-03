from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permissions
from app.db.session import get_db
from app.schemas.inventory import InventoryAdjustRequest, InventoryBalanceRead, InventoryLedgerRead
from app.services import inventory as inventory_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/balance", response_model=list[InventoryBalanceRead], dependencies=[Depends(require_permissions("view_inventory"))])
def get_balance(
    warehouse_id: int | None = None,
    sku_id: int | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    balances = inventory_service.get_balance(db, warehouse_id=warehouse_id, sku_id=sku_id)
    return [InventoryBalanceRead.model_validate(balance) for balance in balances]


@router.get("/ledger", response_model=list[InventoryLedgerRead], dependencies=[Depends(require_permissions("view_inventory"))])
def get_ledger(
    sku_id: int | None = None,
    ref_no: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    entries = inventory_service.get_ledger(db, sku_id=sku_id, ref_no=ref_no)
    return [InventoryLedgerRead.model_validate(entry) for entry in entries]


@router.post("/adjust", response_model=InventoryBalanceRead, dependencies=[Depends(require_permissions("adjust_inventory"))])
def adjust_inventory(
    payload: InventoryAdjustRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    try:
        balance = inventory_service.adjust_inventory(
            db,
            warehouse_id=payload.warehouse_id,
            location_id=payload.location_id,
            sku_id=payload.sku_id,
            qty=payload.qty,
            reason=payload.reason,
            ref_no=payload.ref_no,
            idempotency_key=idempotency_key or payload.idempotency_key,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return InventoryBalanceRead.model_validate(balance)
