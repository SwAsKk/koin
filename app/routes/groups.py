from fastapi import APIRouter, HTTPException, Depends
from typing import List
from db.funcs import DataBase
from shapes import (
    GroupRequest, GroupResponse, GroupMemberRequest, GroupMemberResponse,
    GroupWithMembers, GroupUpdate
)

router = APIRouter()

@router.post("/groups", response_model=GroupResponse)
def create_group(group: GroupRequest, user_id: int):
    """Создать новую группу"""
    try:
        # Создаем группу
        group_data = DataBase.cursor.execute(
            "INSERT INTO groups (name, description, created_by) VALUES (%s, %s, %s) RETURNING id, name, description, created_by, created_at",
            (group.name, group.description, user_id)
        )
        DataBase.connection.commit()
        
        # Получаем созданную группу
        group_result = DataBase.cursor.execute(
            "SELECT g.*, u.name as creator_name FROM groups g JOIN users u ON g.created_by = u.id WHERE g.id = %s",
            (group_data[0],)
        )
        group_info = DataBase.cursor.fetchone()
        
        # Добавляем создателя как участника с ролью owner
        DataBase.cursor.execute(
            "INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, 'owner')",
            (group_info[0], user_id)
        )
        DataBase.connection.commit()
        
        return GroupResponse(
            id=group_info[0],
            name=group_info[1],
            description=group_info[2],
            created_by=group_info[3],
            creator_name=group_info[4],
            is_active=group_info[5],
            created_at=group_info[6]
        )
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при создании группы: {str(e)}")

@router.get("/groups", response_model=List[GroupResponse])
def get_user_groups(user_id: int):
    """Получить все группы пользователя"""
    try:
        DataBase.cursor.execute(
            "SELECT g.*, gm.role, u.name as creator_name FROM groups g JOIN group_members gm ON g.id = gm.group_id JOIN users u ON g.created_by = u.id WHERE gm.user_id = %s AND g.is_active = TRUE ORDER BY g.created_at DESC",
            (user_id,)
        )
        groups = DataBase.cursor.fetchall()
        
        return [
            GroupResponse(
                id=group[0], name=group[1], description=group[2], created_by=group[3],
                creator_name=group[5], is_active=group[4], created_at=group[6]
            )
            for group in groups
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении групп: {str(e)}")

@router.get("/groups/{group_id}", response_model=GroupWithMembers)
def get_group(group_id: int, user_id: int):
    """Получить информацию о группе с участниками"""
    try:
        # Проверяем, что пользователь является участником группы
        DataBase.cursor.execute(
            "SELECT 1 FROM group_members WHERE group_id = %s AND user_id = %s",
            (group_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=403, detail="Доступ запрещен")
        
        # Получаем информацию о группе
        DataBase.cursor.execute(
            "SELECT g.*, u.name as creator_name FROM groups g JOIN users u ON g.created_by = u.id WHERE g.id = %s AND g.is_active = TRUE",
            (group_id,)
        )
        group_info = DataBase.cursor.fetchone()
        if not group_info:
            raise HTTPException(status_code=404, detail="Группа не найдена")
        
        # Получаем участников группы
        DataBase.cursor.execute(
            "SELECT gm.*, u.name, u.email FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s ORDER BY gm.joined_at",
            (group_id,)
        )
        members = DataBase.cursor.fetchall()
        
        return GroupWithMembers(
            id=group_info[0],
            name=group_info[1],
            description=group_info[2],
            created_by=group_info[3],
            creator_name=group_info[4],
            is_active=group_info[5],
            created_at=group_info[6],
            members=[
                GroupMemberResponse(
                    id=member[0], group_id=member[1], user_id=member[2],
                    role=member[3], name=member[4], email=member[5], joined_at=member[6]
                )
                for member in members
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении группы: {str(e)}")

@router.post("/groups/{group_id}/members", response_model=GroupMemberResponse)
def add_group_member(group_id: int, member: GroupMemberRequest, user_id: int):
    """Добавить участника в группу"""
    try:
        # Проверяем, что пользователь является владельцем или админом группы
        DataBase.cursor.execute(
            "SELECT role FROM group_members WHERE group_id = %s AND user_id = %s",
            (group_id, user_id)
        )
        user_role = DataBase.cursor.fetchone()
        if not user_role or user_role[0] not in ['owner', 'admin']:
            raise HTTPException(status_code=403, detail="Недостаточно прав для добавления участников")
        
        # Проверяем, что группа существует и активна
        DataBase.cursor.execute(
            "SELECT 1 FROM groups WHERE id = %s AND is_active = TRUE",
            (group_id,)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=404, detail="Группа не найдена")
        
        # Добавляем участника
        DataBase.cursor.execute(
            "INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, %s) RETURNING id, group_id, user_id, role, joined_at",
            (group_id, member.user_id, member.role)
        )
        DataBase.connection.commit()
        
        # Получаем информацию о добавленном участнике
        DataBase.cursor.execute(
            "SELECT gm.*, u.name, u.email FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.id = %s",
            (DataBase.cursor.fetchone()[0],)
        )
        member_info = DataBase.cursor.fetchone()
        
        return GroupMemberResponse(
            id=member_info[0], group_id=member_info[1], user_id=member_info[2],
            role=member_info[3], name=member_info[4], email=member_info[5], joined_at=member_info[6]
        )
    except HTTPException:
        raise
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении участника: {str(e)}")

@router.put("/groups/{group_id}", response_model=GroupResponse)
def update_group(group_id: int, group_update: GroupUpdate, user_id: int):
    """Обновить информацию о группе"""
    try:
        # Проверяем, что пользователь является владельцем группы
        DataBase.cursor.execute(
            "SELECT 1 FROM group_members WHERE group_id = %s AND user_id = %s AND role = 'owner'",
            (group_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=403, detail="Только владелец может изменять группу")
        
        # Формируем SQL для обновления
        update_fields = []
        update_values = []
        
        if group_update.name is not None:
            update_fields.append("name = %s")
            update_values.append(group_update.name)
        
        if group_update.description is not None:
            update_fields.append("description = %s")
            update_values.append(group_update.description)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="Нет полей для обновления")
        
        update_values.append(group_id)
        update_values.append(user_id)
        
        sql = f"UPDATE groups SET {', '.join(update_fields)} WHERE id = %s AND created_by = %s RETURNING id, name, description, created_by, created_at, is_active"
        
        DataBase.cursor.execute(sql, update_values)
        DataBase.connection.commit()
        
        updated_group = DataBase.cursor.fetchone()
        if not updated_group:
            raise HTTPException(status_code=404, detail="Группа не найдена")
        
        return GroupResponse(
            id=updated_group[0], name=updated_group[1], description=updated_group[2],
            created_by=updated_group[3], creator_name="", is_active=updated_group[5], created_at=updated_group[4]
        )
    except HTTPException:
        raise
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении группы: {str(e)}")

@router.delete("/groups/{group_id}")
def delete_group(group_id: int, user_id: int):
    """Удалить группу (деактивировать)"""
    try:
        # Проверяем, что пользователь является владельцем группы
        DataBase.cursor.execute(
            "SELECT 1 FROM group_members WHERE group_id = %s AND user_id = %s AND role = 'owner'",
            (group_id, user_id)
        )
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=403, detail="Только владелец может удалять группу")
        
        # Деактивируем группу
        DataBase.cursor.execute(
            "UPDATE groups SET is_active = FALSE WHERE id = %s RETURNING id",
            (group_id,)
        )
        DataBase.connection.commit()
        
        if not DataBase.cursor.fetchone():
            raise HTTPException(status_code=404, detail="Группа не найдена")
        
        return {"message": "Группа успешно удалена"}
    except HTTPException:
        raise
    except Exception as e:
        DataBase.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении группы: {str(e)}") 