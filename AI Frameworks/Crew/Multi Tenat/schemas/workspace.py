from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .auth import UserOut


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=120,
        pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$",
    )


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=1000)


class WorkspaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    description: Optional[str] = None
    plan: str = "free"
    created_at: datetime
    member_count: int = 0
    your_role: str = "user"


class MemberInvite(BaseModel):
    email: EmailStr
    role: str = Field(default="user", min_length=1, max_length=20)


class MemberRoleUpdate(BaseModel):
    role: str = Field(min_length=1, max_length=20)


class MemberOut(BaseModel):
    user: UserOut
    role: str
    status: str
    joined_at: datetime


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    action: str
    entity_type: Optional[str] = None
    metadata_json: dict = {}
    created_at: datetime
    actor_name: Optional[str] = None


class DailyCount(BaseModel):
    date: str
    count: int


class WorkspaceStats(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    your_role: str
    member_count: int
    total_activity: int
    activity_7d: list[DailyCount] = []
