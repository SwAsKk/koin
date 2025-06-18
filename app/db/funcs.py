import psycopg2
import json
from functools import wraps
from config import config

from shapes.deal import DealRequest

from db.fields import (
    DB_user_query,
    DB_deal_query
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
    
    @db_dec
    def create_deal(deal: DealRequest):
        DataBase.cursor.execute(DB_deal_query.NEW_DEAL.value, (deal.name, deal.value, deal.is_equally,))
        deal_id = DataBase.get_one_or_none()

        for i in deal.participants:
            DataBase.cursor.execute(DB_deal_query.NEW_PARTICIPANT.value, (i.user_id, deal_id, i.value))




DataBase.connect()
