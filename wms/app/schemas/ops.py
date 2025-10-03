from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PickTaskLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku_id: int
    from_location_id: int
    qty: int


class PickTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    so_id: int
    task_no: str
    status: str
    picker_id: Optional[int]
    created_at: datetime
    lines: List[PickTaskLineRead]


class ShipmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    so_id: int
    ship_no: str
    status: str
    weight_g: Optional[int]
    parcels: Optional[dict]
    label_file_id: Optional[int]
    tracking_no: Optional[str]
    created_at: datetime
