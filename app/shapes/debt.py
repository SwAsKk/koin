from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DebtResponse(BaseModel):
    id: int
    creditor_id: int
    debtor_id: int
    creditor_name: str
    creditor_email: str
    debtor_name: str
    debtor_email: str
    amount: float
    currency: str
    description: Optional[str]
    expense_id: Optional[int]
    expense_type: Optional[str]
    is_settled: bool
    settled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class DebtSummary(BaseModel):
    owes_total: float
    owed_total: float
    net_balance: float

class DebtSettleRequest(BaseModel):
    debt_id: int

class DebtSettleResponse(BaseModel):
    debt_id: int
    settled_at: datetime
    message: str

class DebtBetweenUsers(BaseModel):
    user1_id: int
    user1_name: str
    user2_id: int
    user2_name: str
    debts: list[DebtResponse] 