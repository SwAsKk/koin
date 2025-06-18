from enum import Enum


class DB_user_query(Enum):
    NEW_USER = """
        INSERT INTO users (name, password) 
        VALUES (%s, %s) RETURNING id, name
    """
    GET_USER = "SELECT id, name FROM users WHERE id = %s"
    ALL_USERS = "SELECT id, name FROM users"
    DELETE_USER = "DELETE FROM users WHERE id = %s RETURNING id"


class DB_trans_query(Enum):
    NEW_TRANS = """
        INSERT INTO trans (user_id, name, type_id, value, description)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    GET_TRANS_BY_USER = "SELECT * FROM trans WHERE user_id = %s"
    DELETE_TRANS = "DELETE FROM trans WHERE id = %s RETURNING id"
    ALL_TRANS = "SELECT * FROM trans"


