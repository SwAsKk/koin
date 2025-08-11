from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

class BudgetRequest(BaseModel):
    name: str
    amount: float
    period: str  # 'monthly', 'yearly'
    start_date: date
    end_date: date
    group_id: Optional[int] = None

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    group_id: Optional[int]
    group_name: Optional[str]
    name: str
    amount: float
    period: str
    start_date: date
    end_date: date
    created_at: datetime

class BudgetCategoryRequest(BaseModel):
    category_id: int
    planned_amount: float

class BudgetCategoryResponse(BaseModel):
    id: int
    budget_id: int
    category_id: int
    category_name: str
    category_icon: Optional[str]
    category_color: Optional[str]
    planned_amount: float
    created_at: datetime

class BudgetWithCategories(BaseModel):
    id: int
    user_id: int
    group_id: Optional[int]
    group_name: Optional[str]
    name: str
    amount: float
    period: str
    start_date: date
    end_date: date
    created_at: datetime
    categories: List[BudgetCategoryResponse]

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    period: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None 