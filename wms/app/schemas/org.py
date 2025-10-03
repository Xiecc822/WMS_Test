from typing import Optional

from pydantic import BaseModel, ConfigDict


class WarehouseBase(BaseModel):
    code: str
    name: str
    address_json: Optional[dict] = None
    is_active: bool = True


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseRead(WarehouseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class LocationBase(BaseModel):
    warehouse_id: int
    code: str
    type: str = "STORAGE"
    is_active: bool = True


class LocationCreate(LocationBase):
    pass


class LocationRead(LocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SupplierBase(BaseModel):
    code: str
    name: str
    contact_json: Optional[dict] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierRead(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CustomerBase(BaseModel):
    code: str
    name: str
    contact_json: Optional[dict] = None
    ship_to_json: Optional[dict] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
