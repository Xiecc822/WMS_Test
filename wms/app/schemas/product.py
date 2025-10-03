from typing import Optional

from pydantic import BaseModel, ConfigDict


class SKUBase(BaseModel):
    code: str
    name: str
    barcodes: Optional[list[str]] = None
    uom: str = "EA"
    weight_g: Optional[int] = None
    length_mm: Optional[int] = None
    width_mm: Optional[int] = None
    height_mm: Optional[int] = None
    image_file_id: Optional[int] = None
    is_active: bool = True


class SKUCreate(SKUBase):
    pass


class SKURead(SKUBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
