
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.funcs import DBTransaction

router = APIRouter()

class TransCreate(BaseModel):
    user_id: int
    name: str
    type_id: int
    value: int
    description: str

class TransOut(BaseModel):
    id: int
    name: str
    type_id: int
    value: int
    description: str

@router.post("/transactions", response_model=TransOut)
def create_transaction(trans: TransCreate):
    created = DBTransaction.create_transaction(
        trans.user_id, trans.name, trans.type_id, trans.value, trans.description
    )
    return created

@router.get("/transactions/user/{user_id}", response_model=list[TransOut])
def get_user_transactions(user_id: int):
    return DBTransaction.get_transactions_by_user(user_id)

@router.delete("/transactions/{trans_id}", response_model=dict)
def delete_transaction(trans_id: int):
    deleted = DBTransaction.delete_transaction(trans_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"deleted_id": deleted["id"]}
