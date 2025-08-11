from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from db.funcs import DataBase
from shapes import (
    DebtResponse, DebtSummary, DebtSettleRequest, DebtSettleResponse, DebtBetweenUsers
)

router = APIRouter()

@router.get("/debts", response_model=List[DebtResponse])
def get_user_debts(user_id: int):
    """Получить все долги пользователя"""
    try:
        DataBase.cursor.execute(
            "SELECT d.*, u1.name as creditor_name, u1.email as creditor_email, u2.name as debtor_name, u2.email as debtor_email FROM debts d JOIN users u1 ON d.creditor_id = u1.id JOIN users u2 ON d.debtor_id = u2.id WHERE (d.creditor_id = %s OR d.debtor_id = %s) AND d.is_settled = FALSE ORDER BY d.created_at DESC",
            (user_id, user_id)
        )
        debts = DataBase.cursor.fetchall()
        
        return [
            DebtResponse(
                id=debt[0], creditor_id=debt[1], debtor_id=debt[2], amount=debt[3],
                currency=debt[4], description=debt[5], expense_id=debt[6], expense_type=debt[7],
                is_settled=debt[8], settled_at=debt[9], created_at=debt[10], updated_at=debt[11],
                creditor_name=debt[12], creditor_email=debt[13], debtor_name=debt[14], debtor_email=debt[15]
            )
            for debt in debts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении долгов: {str(e)}")

@router.get("/debts/summary", response_model=DebtSummary)
def get_user_debt_summary(user_id: int):
    """Получить сводку по долгам пользователя"""
    try:
        DataBase.cursor.execute(
            "SELECT * FROM get_user_debts_summary(%s)",
            (user_id,)
        )
        summary = DataBase.cursor.fetchone()
        
        if not summary:
            return DebtSummary(owes_total=0.0, owed_total=0.0, net_balance=0.0)
        
        return DebtSummary(
            owes_total=summary[0],
            owed_total=summary[1],
            net_balance=summary[2]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении сводки по долгам: {str(e)}")

@router.get("/debts/between/{other_user_id}", response_model=DebtBetweenUsers)
def get_debts_between_users(user_id: int, other_user_id: int):
    """Получить долги между двумя пользователями"""
    try:
        DataBase.cursor.execute(
            "SELECT d.*, u1.name as creditor_name, u1.email as creditor_email, u2.name as debtor_name, u2.email as debtor_email FROM debts d JOIN users u1 ON d.creditor_id = u1.id JOIN users u2 ON d.debtor_id = u2.id WHERE ((d.creditor_id = %s AND d.debtor_id = %s) OR (d.creditor_id = %s AND d.debtor_id = %s)) AND d.is_settled = FALSE ORDER BY d.created_at DESC",
            (user_id, other_user_id, other_user_id, user_id)
        )
        debts = DataBase.cursor.fetchall()
        
        # Получаем имена пользователей
        DataBase.cursor.execute(
            "SELECT id, name FROM users WHERE id IN (%s, %s)",
            (user_id, other_user_id)
        )
        users = DataBase.cursor.fetchall()
        user_names = {user[0]: user[1] for user in users}
        
        return DebtBetweenUsers(
            user1_id=user_id,
            user1_name=user_names.get(user_id, ""),
            user2_id=other_user_id,
            user2_name=user_names.get(other_user_id, ""),
            debts=[
                DebtResponse(
                    id=debt[0], creditor_id=debt[1], debtor_id=debt[2], amount=debt[3],
                    currency=debt[4], description=debt[5], expense_id=debt[6], expense_type=debt[7],
                    is_settled=debt[8], settled_at=debt[9], created_at=debt[10], updated_at=debt[11],
                    creditor_name=debt[12], creditor_email=debt[13], debtor_name=debt[14], debtor_email=debt[15]
                )
                for debt in debts
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении долгов между пользователями: {str(e)}")

@router.post("/debts/{debt_id}/settle", response_model=DebtSettleResponse)
def settle_debt(debt_id: int, user_id: int):
    """Погасить долг"""
    try:
        # Проверяем, что пользователь является участником долга
        DataBase.cursor.execute(
            "SELECT 1 FROM debts WHERE id = %s AND (creditor_id = %s OR debtor_id = %s) AND is_settled = FALSE",
            (debt_id, user_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=403, detail="Доступ запрещен или долг уже погашен")
        
        # Погашаем долг
        DataBase.cursor.execute(
            "UPDATE debts SET is_settled = TRUE, settled_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING id",
            (debt_id,)
        )
        DataBase.connection.commit()
        
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=404, detail="Долг не найден")
        
        return DebtSettleResponse(
            debt_id=debt_id,
            settled_at=datetime.now(),
            message="Долг успешно погашен"
        )
    except HTTPException:
        raise
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при погашении долга: {str(e)}")

@router.get("/debts/group/{group_id}", response_model=List[DebtResponse])
def get_group_debts(group_id: int, user_id: int):
    """Получить долги в группе"""
    try:
        # Проверяем, что пользователь является участником группы
        DataBase.cursor.execute(
            "SELECT 1 FROM group_members WHERE group_id = %s AND user_id = %s",
            (group_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=403, detail="Доступ запрещен")
        
        # Получаем долги в группе
        DataBase.cursor.execute(
            """
            SELECT DISTINCT d.*, u1.name as creditor_name, u1.email as creditor_email, 
                   u2.name as debtor_name, u2.email as debtor_email
            FROM debts d 
            JOIN users u1 ON d.creditor_id = u1.id 
            JOIN users u2 ON d.debtor_id = u2.id
            JOIN group_members gm1 ON d.creditor_id = gm1.user_id
            JOIN group_members gm2 ON d.debtor_id = gm2.user_id
            WHERE gm1.group_id = %s AND gm2.group_id = %s AND d.is_settled = FALSE
            ORDER BY d.created_at DESC
            """,
            (group_id, group_id)
        )
        debts = DataBase.cursor.fetchall()
        
        return [
            DebtResponse(
                id=debt[0], creditor_id=debt[1], debtor_id=debt[2], amount=debt[3],
                currency=debt[4], description=debt[5], expense_id=debt[6], expense_type=debt[7],
                is_settled=debt[8], settled_at=debt[9], created_at=debt[10], updated_at=debt[11],
                creditor_name=debt[12], creditor_email=debt[13], debtor_name=debt[14], debtor_email=debt[15]
            )
            for debt in debts
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении долгов группы: {str(e)}")

@router.get("/debts/trip/{trip_id}", response_model=List[DebtResponse])
def get_trip_debts(trip_id: int, user_id: int):
    """Получить долги в поездке"""
    try:
        # Проверяем, что пользователь является участником поездки
        DataBase.cursor.execute(
            "SELECT 1 FROM trip_participants WHERE trip_id = %s AND user_id = %s",
            (trip_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=403, detail="Доступ запрещен")
        
        # Получаем долги в поездке
        DataBase.cursor.execute(
            """
            SELECT d.*, u1.name as creditor_name, u1.email as creditor_email, 
                   u2.name as debtor_name, u2.email as debtor_email
            FROM debts d 
            JOIN users u1 ON d.creditor_id = u1.id 
            JOIN users u2 ON d.debtor_id = u2.id
            JOIN trip_participants tp1 ON d.creditor_id = tp1.user_id
            JOIN trip_participants tp2 ON d.debtor_id = tp2.user_id
            WHERE tp1.trip_id = %s AND tp2.trip_id = %s AND d.expense_type = 'trip_expense' 
            AND d.expense_id IN (SELECT id FROM trip_expenses WHERE trip_id = %s)
            AND d.is_settled = FALSE
            ORDER BY d.created_at DESC
            """,
            (trip_id, trip_id, trip_id)
        )
        debts = DataBase.cursor.fetchall()
        
        return [
            DebtResponse(
                id=debt[0], creditor_id=debt[1], debtor_id=debt[2], amount=debt[3],
                currency=debt[4], description=debt[5], expense_id=debt[6], expense_type=debt[7],
                is_settled=debt[8], settled_at=debt[9], created_at=debt[10], updated_at=debt[11],
                creditor_name=debt[12], creditor_email=debt[13], debtor_name=debt[14], debtor_email=debt[15]
            )
            for debt in debts
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении долгов поездки: {str(e)}") 