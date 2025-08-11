from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BankAccountRequest(BaseModel):
    name: str
    account_number: Optional[str] = None
    balance: float = 0.0
    currency: str = "RUB"
    bank_name: Optional[str] = None

class BankAccountResponse(BaseModel):
    id: int
    user_id: int
    name: str
    account_number: Optional[str]
    balance: float
    currency: str
    bank_name: Optional[str]
    is_active: bool
    created_at: datetime

class BankAccountUpdate(BaseModel):
    name: Optional[str] = None
    account_number: Optional[str] = None
    currency: Optional[str] = None
    bank_name: Optional[str] = None

class BankAccountBalance(BaseModel):
    account_id: int
    account_name: str
    current_balance: float
    currency: str 