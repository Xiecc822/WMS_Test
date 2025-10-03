from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PurchaseOrderLineCreate(BaseModel):
    sku_id: int
    qty_ordered: int


class PurchaseOrderCreate(BaseModel):
    po_no: str
    supplier_id: int
    lines: List[PurchaseOrderLineCreate]


class PurchaseOrderLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku_id: int
    qty_ordered: int
    qty_received: int


class PurchaseOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    po_no: str
    supplier_id: int
    status: str
    created_at: datetime
    lines: List[PurchaseOrderLineRead]


class SalesOrderLineCreate(BaseModel):
    sku_id: int
    qty_ordered: int


class SalesOrderCreate(BaseModel):
    so_no: str
    customer_id: int
    ship_to_json: Optional[dict] = None
    carrier_service: Optional[str] = None
    lines: List[SalesOrderLineCreate]


class SalesOrderLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku_id: int
    qty_ordered: int
    qty_allocated: int
    qty_shipped: int


class SalesOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    so_no: str
    customer_id: int
    status: str
    created_at: datetime
    ship_to_json: Optional[dict]
    carrier_service: Optional[str]
    lines: List[SalesOrderLineRead]
