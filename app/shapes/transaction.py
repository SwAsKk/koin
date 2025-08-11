from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class TransCreate(BaseModel):
    user_id: int
    name: str
    type_id: int
    value: float
    description: Optional[str] = None
    is_shared: bool = False
    group_id: Optional[int] = None
    bank_account_id: Optional[int] = None
    investment_account_id: Optional[int] = None
    date: Optional[date] = None

class TransOut(BaseModel):
    id: int
    user_id: int
    name: str
    type_id: int
    value: float
    description: Optional[str]
    is_shared: bool
    group_id: Optional[int]
    bank_account_id: Optional[int]
    investment_account_id: Optional[int]
    date: date
    created_at: datetime
    category_name: Optional[str]
    category_icon: Optional[str]
    category_color: Optional[str]
    category_is_income: Optional[bool]
    bank_account_name: Optional[str]
    investment_account_name: Optional[str]

class TransUpdate(BaseModel):
    name: Optional[str] = None
    type_id: Optional[int] = None
    value: Optional[float] = None
    description: Optional[str] = None
    is_shared: Optional[bool] = None
    group_id: Optional[int] = None
    bank_account_id: Optional[int] = None
    investment_account_id: Optional[int] = None
    date: Optional[date] = None

class SharedTransResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    name: str
    type_id: int
    value: float
    description: Optional[str]
    is_shared: bool
    group_id: int
    date: date
    created_at: datetime
    category_name: Optional[str]
    category_icon: Optional[str]
    category_color: Optional[str]

class TransactionSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int 