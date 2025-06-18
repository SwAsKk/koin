import psycopg2
import json
from functools import wraps
from config import config

from db.fields import (
    DB_user_query,
    DB_trans_query
    )


class DataBase:
    connection = None
    cursor = None

    @staticmethod
    def connect():
        DataBase.connection = psycopg2.connect(
            dbname=config.dbname,
            user=config.user,
            password=config.password,
            host=config.host,
            port=config.port
        )
        DataBase.cursor = DataBase.connection.cursor()

    @staticmethod
    def get_one_or_none():
        res = DataBase.cursor.fetchone()
        res = res[0] if res else None
        return res

    @staticmethod
    def cursor_to_dict():
        desc = DataBase.cursor.description
        column_names = [col[0] for col in desc]
        res = [dict(zip(column_names, row)) for row in DataBase.cursor.fetchall()]
        return res

    @staticmethod
    def db_dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except psycopg2.Error:
                DataBase.connection.rollback()
                raise

        return wrapper
    
    @db_dec
    def create_user(name):
        DataBase.cursor.execute(DB_user_query.NEW_USER.value, (name,))
        DataBase.connection.commit()

        return DataBase.get_one_or_none()

class DBTransaction:

    @staticmethod
    @DataBase.db_dec
    def create_transaction(user_id: int, name: str, type_id: int, value: int, description: str):
        DataBase.cursor.execute(DB_trans_query.NEW_TRANS.value, (user_id, name, type_id, value, description))
        return DataBase.get_one()

    @staticmethod
    @DataBase.db_dec
    def get_transactions_by_user(user_id: int):
        DataBase.cursor.execute(DB_trans_query.GET_TRANS_BY_USER.value, (user_id,))
        return DataBase.get_all()

    @staticmethod
    @DataBase.db_dec
    def delete_transaction(trans_id: int):
        DataBase.cursor.execute(DB_trans_query.DELETE_TRANS.value, (trans_id,))
        return DataBase.get_one()


DataBase.connect()
