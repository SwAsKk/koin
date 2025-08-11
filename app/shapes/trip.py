from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

class TripRequest(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    group_id: Optional[int] = None

class TripResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    created_by: int
    creator_name: str
    group_id: Optional[int]
    group_name: Optional[str]
    is_active: bool
    created_at: datetime

class TripParticipantRequest(BaseModel):
    user_id: int

class TripParticipantResponse(BaseModel):
    id: int
    trip_id: int
    user_id: int
    name: str
    email: str
    joined_at: datetime

class TripExpenseRequest(BaseModel):
    name: str
    amount: float
    currency: str = "RUB"
    description: Optional[str] = None
    date: Optional[date] = None

class TripExpenseResponse(BaseModel):
    id: int
    trip_id: int
    name: str
    amount: float
    currency: str
    paid_by: int
    payer_name: str
    description: Optional[str]
    date: date
    created_at: datetime

class TripWithParticipants(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    created_by: int
    creator_name: str
    group_id: Optional[int]
    group_name: Optional[str]
    is_active: bool
    created_at: datetime
    participants: List[TripParticipantResponse]

class TripWithExpenses(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    created_by: int
    creator_name: str
    group_id: Optional[int]
    group_name: Optional[str]
    is_active: bool
    created_at: datetime
    expenses: List[TripExpenseResponse]

class TripUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None 