from enum import Enum


class DB_user_query(Enum):
    NEW_USER = """
    INSERT INTO users 
        (name)
    VALUES
        (%s)
    RETURNING id
    """


class DB_deal_query(Enum):
    NEW_DEAL = """
    INSERT INTO users 
        (name, value, is_equally, timestamp)
    VALUES
        (%s, %s, %s, now())
    RETURNING id
    """

    NEW_PARTICIPANT = """
    INSERT INTO users 
        (user_id, deal_id, value)
    VALUES
        (%s, %s, %s)
    RETURNING id
    """