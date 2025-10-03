from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    bucket: str
    mime: str
    size: int
    uploader_id: Optional[int]
    created_at: datetime
    meta_json: Optional[dict]
