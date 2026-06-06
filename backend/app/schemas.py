from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    id: int
    username: str
    status: str
    roles: list[str]
    permissions: list[str]

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str = Field(min_length=6)
    status: str = "active"
    role_ids: list[int] = []


class UserUpdate(BaseModel):
    status: Optional[str] = None
    password: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    status: str
    created_at: datetime
    roles: list[str] = []

    class Config:
        from_attributes = True


class RoleAssign(BaseModel):
    role_ids: list[int]


class RoleCreate(BaseModel):
    role_name: str
    description: Optional[str] = None


class RoleOut(BaseModel):
    id: int
    role_name: str
    description: Optional[str]
    permissions: list[str] = []

    class Config:
        from_attributes = True


class PermissionOut(BaseModel):
    id: int
    permission_code: str
    permission_name: str

    class Config:
        from_attributes = True


class RolePermissionAssign(BaseModel):
    permission_ids: list[int]


class AssetOut(BaseModel):
    id: int
    name: str
    asset_type: str
    description: Optional[str]
    owner_id: Optional[int]
    owner_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    file_ext: str = ""
    previewable: bool = True

    class Config:
        from_attributes = True


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    asset_type: Optional[str] = None
    description: Optional[str] = None


class LogOut(BaseModel):
    id: int
    user_id: Optional[int]
    username: Optional[str] = None
    action: str
    target_type: Optional[str]
    target_id: Optional[str]
    result: str
    detail: Optional[str]
    ip: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    user_count: int
    asset_count: int
    role_count: int
    permission_count: int
    log_count: int
    recent_logs: list[LogOut]
