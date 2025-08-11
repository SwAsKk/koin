from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class GroupRequest(BaseModel):
    name: str
    description: Optional[str] = None

class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_by: int
    creator_name: str
    is_active: bool
    created_at: datetime

class GroupMemberRequest(BaseModel):
    user_id: int
    role: str = "member"  # 'owner', 'admin', 'member'

class GroupMemberResponse(BaseModel):
    id: int
    group_id: int
    user_id: int
    role: str
    name: str
    email: str
    joined_at: datetime

class GroupWithMembers(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_by: int
    creator_name: str
    is_active: bool
    created_at: datetime
    members: List[GroupMemberResponse]

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None 