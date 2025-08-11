from fastapi import APIRouter, HTTPException
from typing import List
from db.funcs import DataBase
from shapes import (
    BankAccountRequest, BankAccountResponse, BankAccountUpdate, BankAccountBalance
)

router = APIRouter()

@router.post("/bank-accounts", response_model=BankAccountResponse)
def create_bank_account(account: BankAccountRequest, user_id: int):
    """Создать новый банковский счет"""
    try:
        DataBase.cursor.execute(
            "INSERT INTO bank_accounts (user_id, name, account_number, balance, currency, bank_name) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, user_id, name, account_number, balance, currency, bank_name, is_active, created_at",
            (user_id, account.name, account.account_number, account.balance, account.currency, account.bank_name)
        )
        DataBase.connection.commit()
        
        account_data = DataBase.cursor.fetchone()
        
        return BankAccountResponse(
            id=account_data[0], user_id=account_data[1], name=account_data[2],
            account_number=account_data[3], balance=account_data[4], currency=account_data[5],
            bank_name=account_data[6], is_active=account_data[7], created_at=account_data[8]
        )
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при создании банковского счета: {str(e)}")

@router.get("/bank-accounts", response_model=List[BankAccountResponse])
def get_user_bank_accounts(user_id: int):
    """Получить все банковские счета пользователя"""
    try:
        DataBase.cursor.execute(
            "SELECT * FROM bank_accounts WHERE user_id = %s AND is_active = TRUE ORDER BY created_at DESC",
            (user_id,)
        )
        accounts = DataBase.cursor.fetchall()
        
        return [
            BankAccountResponse(
                id=account[0], user_id=account[1], name=account[2],
                account_number=account[3], balance=account[4], currency=account[5],
                bank_name=account[6], is_active=account[7], created_at=account[8]
            )
            for account in accounts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении банковских счетов: {str(e)}")

@router.get("/bank-accounts/{account_id}", response_model=BankAccountResponse)
def get_bank_account(account_id: int, user_id: int):
    """Получить информацию о банковском счете"""
    try:
        DataBase.cursor.execute(
            "SELECT * FROM bank_accounts WHERE id = %s AND user_id = %s AND is_active = TRUE",
            (account_id, user_id)
        )
        account = DataBase.cursor.fetchone()
        
        if not account:
            raise HTTPException(status_code=404, detail="Банковский счет не найден")
        
        return BankAccountResponse(
            id=account[0], user_id=account[1], name=account[2],
            account_number=account[3], balance=account[4], currency=account[5],
            bank_name=account[6], is_active=account[7], created_at=account[8]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении банковского счета: {str(e)}")

@router.put("/bank-accounts/{account_id}", response_model=BankAccountResponse)
def update_bank_account(account_id: int, account_update: BankAccountUpdate, user_id: int):
    """Обновить информацию о банковском счете"""
    try:
        # Проверяем, что счет принадлежит пользователю
        DataBase.cursor.execute(
            "SELECT 1 FROM bank_accounts WHERE id = %s AND user_id = %s AND is_active = TRUE",
            (account_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=404, detail="Банковский счет не найден")
        
        # Формируем SQL для обновления
        update_fields = []
        update_values = []
        
        if account_update.name is not None:
            update_fields.append("name = %s")
            update_values.append(account_update.name)
        
        if account_update.account_number is not None:
            update_fields.append("account_number = %s")
            update_values.append(account_update.account_number)
        
        if account_update.currency is not None:
            update_fields.append("currency = %s")
            update_values.append(account_update.currency)
        
        if account_update.bank_name is not None:
            update_fields.append("bank_name = %s")
            update_values.append(account_update.bank_name)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="Нет полей для обновления")
        
        update_values.append(account_id)
        update_values.append(user_id)
        
        sql = f"UPDATE bank_accounts SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s RETURNING id, user_id, name, account_number, balance, currency, bank_name, is_active, created_at"
        
        DataBase.cursor.execute(sql, update_values)
        DataBase.connection.commit()
        
        updated_account = DataBase.cursor.fetchone()
        if not updated_account:
            raise HTTPException(status_code=404, detail="Банковский счет не найден")
        
        return BankAccountResponse(
            id=updated_account[0], user_id=updated_account[1], name=updated_account[2],
            account_number=updated_account[3], balance=updated_account[4], currency=updated_account[5],
            bank_name=updated_account[6], is_active=updated_account[7], created_at=updated_account[8]
        )
    except HTTPException:
        raise
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении банковского счета: {str(e)}")

@router.delete("/bank-accounts/{account_id}")
def delete_bank_account(account_id: int, user_id: int):
    """Удалить банковский счет (деактивировать)"""
    try:
        # Проверяем, что счет принадлежит пользователю
        DataBase.cursor.execute(
            "SELECT 1 FROM bank_accounts WHERE id = %s AND user_id = %s AND is_active = TRUE",
            (account_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=404, detail="Банковский счет не найден")
        
        # Проверяем, что на счете нет активных транзакций
        DataBase.cursor.execute(
            "SELECT 1 FROM trans WHERE bank_account_id = %s",
            (account_id,)
        )
        if DataBase.cursor.fetchone():
            raise HTTPException(status_code=400, detail="Нельзя удалить счет с активными транзакциями")
        
        # Деактивируем счет
        DataBase.cursor.execute(
            "UPDATE bank_accounts SET is_active = FALSE WHERE id = %s RETURNING id",
            (account_id,)
        )
        DataBase.connection.commit()
        
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=404, detail="Банковский счет не найден")
        
        return {"message": "Банковский счет успешно удален"}
    except HTTPException:
        raise
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении банковского счета: {str(e)}")

@router.get("/bank-accounts/{account_id}/balance", response_model=BankAccountBalance)
def get_bank_account_balance(account_id: int, user_id: int):
    """Получить текущий баланс банковского счета"""
    try:
        DataBase.cursor.execute(
            "SELECT id, name, balance, currency FROM bank_accounts WHERE id = %s AND user_id = %s AND is_active = TRUE",
            (account_id, user_id)
        )
        account = DataBase.cursor.fetchone()
        
        if not account:
            raise HTTPException(status_code=404, detail="Банковский счет не найден")
        
        return BankAccountBalance(
            account_id=account[0],
            account_name=account[1],
            current_balance=account[2],
            currency=account[3]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении баланса: {str(e)}")

@router.get("/bank-accounts/summary")
def get_user_bank_accounts_summary(user_id: int):
    """Получить сводку по всем банковским счетам пользователя"""
    try:
        DataBase.cursor.execute(
            "SELECT currency, COUNT(*) as accounts_count, SUM(balance) as total_balance FROM bank_accounts WHERE user_id = %s AND is_active = TRUE GROUP BY currency",
            (user_id,)
        )
        summary = DataBase.cursor.fetchall()
        
        return {
            "currencies": [
                {
                    "currency": row[0],
                    "accounts_count": row[1],
                    "total_balance": row[2]
                }
                for row in summary
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении сводки: {str(e)}") 