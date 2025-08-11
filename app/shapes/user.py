from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    is_active: bool

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserWithBalance(BaseModel):
    id: int
    name: str
    email: str
    total_bank_balance: float
    total_investment_balance: float
    total_balance: float
