from enum import Enum


class DB_user_query(Enum):
    NEW_USER = """
    INSERT INTO users 
        (name)
    VALUES
        (%s)
    RETURNING id
    """


