from fastapi import APIRouter, HTTPException
from typing import List
from datetime import date
from db.funcs import DataBase
from shapes import (
    TripRequest, TripResponse, TripParticipantRequest, TripParticipantResponse,
    TripExpenseRequest, TripExpenseResponse, TripWithParticipants, TripWithExpenses, TripUpdate
)

router = APIRouter()

@router.post("/trips", response_model=TripResponse)
def create_trip(trip: TripRequest, user_id: int):
    """Создать новую поездку"""
    try:
        # Создаем поездку
        DataBase.cursor.execute(
            "INSERT INTO trips (name, description, start_date, end_date, created_by, group_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, name, description, start_date, end_date, created_by, group_id, created_at",
            (trip.name, trip.description, trip.start_date, trip.end_date, user_id, trip.group_id)
        )
        DataBase.connection.commit()
        
        trip_data = DataBase.cursor.fetchone()
        
        # Добавляем создателя как участника
        DataBase.cursor.execute(
            "INSERT INTO trip_participants (trip_id, user_id) VALUES (%s, %s)",
            (trip_data[0], user_id)
        )
        DataBase.connection.commit()
        
        # Получаем полную информацию о поездке
        DataBase.cursor.execute(
            "SELECT t.*, u.name as creator_name, g.name as group_name FROM trips t JOIN users u ON t.created_by = u.id LEFT JOIN groups g ON t.group_id = g.id WHERE t.id = %s",
            (trip_data[0],)
        )
        trip_info = DataBase.cursor.fetchone()
        
        return TripResponse(
            id=trip_info[0], name=trip_info[1], description=trip_info[2],
            start_date=trip_info[3], end_date=trip_info[4], created_by=trip_info[5],
            creator_name=trip_info[6], group_id=trip_info[7], group_name=trip_info[8],
            is_active=trip_info[9], created_at=trip_info[10]
        )
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при создании поездки: {str(e)}")

@router.get("/trips", response_model=List[TripResponse])
def get_user_trips(user_id: int):
    """Получить все поездки пользователя"""
    try:
        DataBase.cursor.execute(
            "SELECT t.*, u.name as creator_name, g.name as group_name FROM trips t JOIN users u ON t.created_by = u.id LEFT JOIN groups g ON t.group_id = g.id WHERE t.created_by = %s OR t.id IN (SELECT trip_id FROM trip_participants WHERE user_id = %s) ORDER BY t.start_date DESC, t.created_at DESC",
            (user_id, user_id)
        )
        trips = DataBase.cursor.fetchall()
        
        return [
            TripResponse(
                id=trip[0], name=trip[1], description=trip[2], start_date=trip[3],
                end_date=trip[4], created_by=trip[5], creator_name=trip[6],
                group_id=trip[7], group_name=trip[8], is_active=trip[9], created_at=trip[10]
            )
            for trip in trips
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении поездок: {str(e)}")

@router.get("/trips/{trip_id}", response_model=TripWithParticipants)
def get_trip(trip_id: int, user_id: int):
    """Получить информацию о поездке с участниками"""
    try:
        # Проверяем, что пользователь является участником поездки
        DataBase.cursor.execute(
            "SELECT 1 FROM trip_participants WHERE trip_id = %s AND user_id = %s",
            (trip_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=403, detail="Доступ запрещен")
        
        # Получаем информацию о поездке
        DataBase.cursor.execute(
            "SELECT t.*, u.name as creator_name, g.name as group_name FROM trips t JOIN users u ON t.created_by = u.id LEFT JOIN groups g ON t.group_id = g.id WHERE t.id = %s AND t.is_active = TRUE",
            (trip_id,)
        )
        trip_info = DataBase.cursor.fetchone()
        if not trip_info:
            raise HTTPException(status_code=404, detail="Поездка не найдена")
        
        # Получаем участников поездки
        DataBase.cursor.execute(
            "SELECT tp.*, u.name, u.email FROM trip_participants tp JOIN users u ON tp.user_id = u.id WHERE tp.trip_id = %s ORDER BY tp.joined_at",
            (trip_id,)
        )
        participants = DataBase.cursor.fetchall()
        
        return TripWithParticipants(
            id=trip_info[0], name=trip_info[1], description=trip_info[2],
            start_date=trip_info[3], end_date=trip_info[4], created_by=trip_info[5],
            creator_name=trip_info[6], group_id=trip_info[7], group_name=trip_info[8],
            is_active=trip_info[9], created_at=trip_info[10],
            participants=[
                TripParticipantResponse(
                    id=participant[0], trip_id=participant[1], user_id=participant[2],
                    name=participant[3], email=participant[4], joined_at=participant[5]
                )
                for participant in participants
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении поездки: {str(e)}")

@router.post("/trips/{trip_id}/participants", response_model=TripParticipantResponse)
def add_trip_participant(trip_id: int, participant: TripParticipantRequest, user_id: int):
    """Добавить участника в поездку"""
    try:
        # Проверяем, что пользователь является создателем поездки
        DataBase.cursor.execute(
            "SELECT 1 FROM trips WHERE id = %s AND created_by = %s",
            (trip_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=403, detail="Только создатель может добавлять участников")
        
        # Проверяем, что поездка существует и активна
        DataBase.cursor.execute(
            "SELECT 1 FROM trips WHERE id = %s AND is_active = TRUE",
            (trip_id,)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=404, detail="Поездка не найдена")
        
        # Добавляем участника
        DataBase.cursor.execute(
            "INSERT INTO trip_participants (trip_id, user_id) VALUES (%s, %s) RETURNING id, trip_id, user_id, joined_at",
            (trip_id, participant.user_id)
        )
        DataBase.connection.commit()
        
        # Получаем информацию о добавленном участнике
        DataBase.cursor.execute(
            "SELECT tp.*, u.name, u.email FROM trip_participants tp JOIN users u ON tp.user_id = u.id WHERE tp.id = %s",
            (DataBase.cursor.fetchone()[0],)
        )
        participant_info = DataBase.cursor.fetchone()
        
        return TripParticipantResponse(
            id=participant_info[0], trip_id=participant_info[1], user_id=participant_info[2],
            name=participant_info[3], email=participant_info[4], joined_at=participant_info[5]
        )
    except HTTPException:
        raise
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении участника: {str(e)}")

@router.post("/trips/{trip_id}/expenses", response_model=TripExpenseResponse)
def add_trip_expense(trip_id: int, expense: TripExpenseRequest, user_id: int):
    """Добавить трату в поездку"""
    try:
        # Проверяем, что пользователь является участником поездки
        DataBase.cursor.execute(
            "SELECT 1 FROM trip_participants WHERE trip_id = %s AND user_id = %s",
            (trip_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=403, detail="Доступ запрещен")
        
        # Проверяем, что поездка существует и активна
        DataBase.cursor.execute(
            "SELECT 1 FROM trips WHERE id = %s AND is_active = TRUE",
            (trip_id,)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=404, detail="Поездка не найдена")
        
        # Добавляем трату
        expense_date = expense.date or date.today()
        DataBase.cursor.execute(
            "INSERT INTO trip_expenses (trip_id, name, amount, currency, paid_by, description, date) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id, trip_id, name, amount, currency, paid_by, description, date, created_at",
            (trip_id, expense.name, expense.amount, expense.currency, user_id, expense.description, expense_date)
        )
        DataBase.connection.commit()
        
        expense_data = DataBase.cursor.fetchone()
        
        return TripExpenseResponse(
            id=expense_data[0], trip_id=expense_data[1], name=expense_data[2],
            amount=expense_data[3], currency=expense_data[4], paid_by=expense_data[5],
            description=expense_data[6], date=expense_data[7], created_at=expense_data[8],
            payer_name=""  # Будет заполнено в представлении
        )
    except HTTPException:
        raise
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении траты: {str(e)}")

@router.get("/trips/{trip_id}/expenses", response_model=List[TripExpenseResponse])
def get_trip_expenses(trip_id: int, user_id: int):
    """Получить все траты поездки"""
    try:
        # Проверяем, что пользователь является участником поездки
        DataBase.cursor.execute(
            "SELECT 1 FROM trip_participants WHERE trip_id = %s AND user_id = %s",
            (trip_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=403, detail="Доступ запрещен")
        
        # Получаем траты поездки
        DataBase.cursor.execute(
            "SELECT te.*, u.name as payer_name FROM trip_expenses te JOIN users u ON te.paid_by = u.id WHERE te.trip_id = %s ORDER BY te.date DESC, te.created_at DESC",
            (trip_id,)
        )
        expenses = DataBase.cursor.fetchall()
        
        return [
            TripExpenseResponse(
                id=expense[0], trip_id=expense[1], name=expense[2], amount=expense[3],
                currency=expense[4], paid_by=expense[5], description=expense[6],
                date=expense[7], created_at=expense[8], payer_name=expense[9]
            )
            for expense in expenses
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении трат: {str(e)}")

@router.put("/trips/{trip_id}", response_model=TripResponse)
def update_trip(trip_id: int, trip_update: TripUpdate, user_id: int):
    """Обновить информацию о поездке"""
    try:
        # Проверяем, что пользователь является создателем поездки
        DataBase.cursor.execute(
            "SELECT 1 FROM trips WHERE id = %s AND created_by = %s",
            (trip_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=403, detail="Только создатель может изменять поездку")
        
        # Формируем SQL для обновления
        update_fields = []
        update_values = []
        
        if trip_update.name is not None:
            update_fields.append("name = %s")
            update_values.append(trip_update.name)
        
        if trip_update.description is not None:
            update_fields.append("description = %s")
            update_values.append(trip_update.description)
        
        if trip_update.start_date is not None:
            update_fields.append("start_date = %s")
            update_values.append(trip_update.start_date)
        
        if trip_update.end_date is not None:
            update_fields.append("end_date = %s")
            update_values.append(trip_update.end_date)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="Нет полей для обновления")
        
        update_values.append(trip_id)
        update_values.append(user_id)
        
        sql = f"UPDATE trips SET {', '.join(update_fields)} WHERE id = %s AND created_by = %s RETURNING id, name, description, start_date, end_date, created_by, group_id, created_at, is_active"
        
        DataBase.cursor.execute(sql, update_values)
        DataBase.connection.commit()
        
        updated_trip = DataBase.cursor.fetchone()
        if not updated_trip:
            raise HTTPException(status_code=404, detail="Поездка не найдена")
        
        return TripResponse(
            id=updated_trip[0], name=updated_trip[1], description=updated_trip[2],
            start_date=updated_trip[3], end_date=updated_trip[4], created_by=updated_trip[5],
            creator_name="", group_id=updated_trip[6], group_name="", is_active=updated_trip[8], created_at=updated_trip[7]
        )
    except HTTPException:
        raise
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении поездки: {str(e)}")

@router.delete("/trips/{trip_id}")
def delete_trip(trip_id: int, user_id: int):
    """Удалить поездку (деактивировать)"""
    try:
        # Проверяем, что пользователь является создателем поездки
        DataBase.cursor.execute(
            "SELECT 1 FROM trips WHERE id = %s AND created_by = %s",
            (trip_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=403, detail="Только создатель может удалять поездку")
        
        # Деактивируем поездку
        DataBase.cursor.execute(
            "UPDATE trips SET is_active = FALSE WHERE id = %s RETURNING id",
            (trip_id,)
        )
        DataBase.connection.commit()
        
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=404, detail="Поездка не найдена")
        
        return {"message": "Поездка успешно удалена"}
    except HTTPException:
        raise
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении поездки: {str(e)}") 