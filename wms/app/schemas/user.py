from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.rbac import RoleRead


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    dept_id: Optional[int] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    role_ids: List[int] = Field(default_factory=list)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_superuser: bool
    created_at: datetime
    roles: List[RoleRead]
