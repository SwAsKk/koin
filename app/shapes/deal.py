from pydantic import BaseModel
from typing import List, Optional

class Participant(BaseModel):
    user_id: int
    value: Optional[int] = None

class DealRequest(BaseModel):
    name: str
    value: int
    is_equally: bool
    participants: List[Participant]