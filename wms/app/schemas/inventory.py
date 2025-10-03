from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InventoryBalanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    warehouse_id: int
    sku_id: int
    location_id: int
    on_hand: int
    reserved: int
    available: int


class InventoryLedgerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ts: datetime
    type: str
    qty: int
    warehouse_id: int
    sku_id: int
    location_id: int
    ref_type: Optional[str]
    ref_id: Optional[int]
    ref_no: Optional[str]
    idempotency_key: Optional[str]


class InventoryAdjustRequest(BaseModel):
    warehouse_id: int
    location_id: int
    sku_id: int
    qty: int
    reason: str
    ref_no: Optional[str] = None
    idempotency_key: Optional[str] = None
