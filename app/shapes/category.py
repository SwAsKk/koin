from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoryRequest(BaseModel):
    name: str
    is_income: bool = False
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    is_income: bool
    icon: Optional[str]
    color: Optional[str]
    parent_id: Optional[int]
    parent_name: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    is_income: Optional[bool] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryWithChildren(BaseModel):
    id: int
    name: str
    is_income: bool
    icon: Optional[str]
    color: Optional[str]
    parent_id: Optional[int]
    children: List['CategoryResponse'] = [] 