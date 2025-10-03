from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PermissionBase(BaseModel):
    code: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionRead(PermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: List[int] = Field(default_factory=list)


class RoleRead(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    permissions: List[PermissionRead]
