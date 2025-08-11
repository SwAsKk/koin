from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InvestmentAccountRequest(BaseModel):
    name: str
    account_type: str  # 'brokerage', 'iis', 'deposit', 'crypto'
    balance: float = 0.0
    currency: str = "RUB"
    institution_name: Optional[str] = None

class InvestmentAccountResponse(BaseModel):
    id: int
    user_id: int
    name: str
    account_type: str
    balance: float
    currency: str
    institution_name: Optional[str]
    is_active: bool
    created_at: datetime

class InvestmentAccountUpdate(BaseModel):
    name: Optional[str] = None
    account_type: Optional[str] = None
    currency: Optional[str] = None
    institution_name: Optional[str] = None

class InvestmentAccountBalance(BaseModel):
    account_id: int
    account_name: str
    account_type: str
    current_balance: float
    currency: str 