from enum import Enum


class DB_user_query(Enum):
    NEW_USER = """
        INSERT INTO users (name, password, email) 
        VALUES (%s, %s, %s) RETURNING id, name, email
    """
    GET_USER = "SELECT id, name, email, created_at, is_active FROM users WHERE id = %s"
    GET_USER_BY_EMAIL = "SELECT id, name, password, email, created_at, is_active FROM users WHERE email = %s"
    ALL_USERS = "SELECT id, name, email, created_at, is_active FROM users WHERE is_active = TRUE"
    DELETE_USER = "UPDATE users SET is_active = FALSE WHERE id = %s RETURNING id"
    UPDATE_USER = "UPDATE users SET name = %s, email = %s WHERE id = %s RETURNING id, name, email"


class DB_trans_query(Enum):
    NEW_TRANS = """
        INSERT INTO trans (user_id, name, type_id, value, description, is_shared, group_id, bank_account_id, investment_account_id, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, user_id, name, type_id, value, description, is_shared, group_id, bank_account_id, investment_account_id, date, created_at
    """
    GET_TRANS_BY_USER = """
        SELECT t.*, c.name as category_name, c.icon, c.color, c.is_income,
               ba.name as bank_account_name, ia.name as investment_account_name
        FROM trans t
        LEFT JOIN category c ON t.category_id = c.id
        LEFT JOIN bank_accounts ba ON t.bank_account_id = ba.id
        LEFT JOIN investment_accounts ia ON t.investment_account_id = ia.id
        WHERE t.user_id = %s
        ORDER BY t.date DESC, t.created_at DESC
    """
    GET_SHARED_TRANS_BY_GROUP = """
        SELECT t.*, u.name as user_name, c.name as category_name, c.icon, c.color
        FROM trans t
        JOIN users u ON t.user_id = u.id
        LEFT JOIN category c ON t.category_id = c.id
        WHERE t.group_id = %s AND t.is_shared = TRUE
        ORDER BY t.date DESC, t.created_at DESC
    """
    DELETE_TRANS = "DELETE FROM trans WHERE id = %s RETURNING id"
    ALL_TRANS = """
        SELECT t.*, u.name as user_name, c.name as category_name, c.icon, c.color
        FROM trans t
        JOIN users u ON t.user_id = u.id
        LEFT JOIN category c ON t.category_id = c.id
        ORDER BY t.date DESC, t.created_at DESC
    """
    UPDATE_TRANS = """
        UPDATE trans SET name = %s, type_id = %s, value = %s, description = %s, 
                        is_shared = %s, group_id = %s, bank_account_id = %s, 
                        investment_account_id = %s, date = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s RETURNING id
    """


class DB_bank_account_query(Enum):
    NEW_BANK_ACCOUNT = """
        INSERT INTO bank_accounts (user_id, name, account_number, balance, currency, bank_name)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, user_id, name, account_number, balance, currency, bank_name, created_at
    """
    GET_BANK_ACCOUNTS_BY_USER = """
        SELECT * FROM bank_accounts 
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY created_at DESC
    """
    UPDATE_BANK_ACCOUNT = """
        UPDATE bank_accounts SET name = %s, account_number = %s, currency = %s, bank_name = %s
        WHERE id = %s AND user_id = %s RETURNING id
    """
    DELETE_BANK_ACCOUNT = "UPDATE bank_accounts SET is_active = FALSE WHERE id = %s RETURNING id"


class DB_investment_account_query(Enum):
    NEW_INVESTMENT_ACCOUNT = """
        INSERT INTO investment_accounts (user_id, name, account_type, balance, currency, institution_name)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, user_id, name, account_type, balance, currency, institution_name, created_at
    """
    GET_INVESTMENT_ACCOUNTS_BY_USER = """
        SELECT * FROM investment_accounts 
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY created_at DESC
    """
    UPDATE_INVESTMENT_ACCOUNT = """
        UPDATE investment_accounts SET name = %s, account_type = %s, currency = %s, institution_name = %s
        WHERE id = %s AND user_id = %s RETURNING id
    """
    DELETE_INVESTMENT_ACCOUNT = "UPDATE investment_accounts SET is_active = FALSE WHERE id = %s RETURNING id"


class DB_group_query(Enum):
    NEW_GROUP = """
        INSERT INTO groups (name, description, created_by)
        VALUES (%s, %s, %s)
        RETURNING id, name, description, created_by, created_at
    """
    GET_GROUP_BY_ID = """
        SELECT g.*, u.name as creator_name
        FROM groups g
        JOIN users u ON g.created_by = u.id
        WHERE g.id = %s AND g.is_active = TRUE
    """
    GET_GROUPS_BY_USER = """
        SELECT g.*, gm.role, u.name as creator_name
        FROM groups g
        JOIN group_members gm ON g.id = gm.group_id
        JOIN users u ON g.created_by = u.id
        WHERE gm.user_id = %s AND g.is_active = TRUE
        ORDER BY g.created_at DESC
    """
    ADD_GROUP_MEMBER = """
        INSERT INTO group_members (group_id, user_id, role)
        VALUES (%s, %s, %s)
        RETURNING id, group_id, user_id, role, joined_at
    """
    GET_GROUP_MEMBERS = """
        SELECT gm.*, u.name, u.email
        FROM group_members gm
        JOIN users u ON gm.user_id = u.id
        WHERE gm.group_id = %s
        ORDER BY gm.joined_at
    """
    UPDATE_GROUP = """
        UPDATE groups SET name = %s, description = %s
        WHERE id = %s AND created_by = %s RETURNING id
    """
    DELETE_GROUP = "UPDATE groups SET is_active = FALSE WHERE id = %s RETURNING id"


class DB_trip_query(Enum):
    NEW_TRIP = """
        INSERT INTO trips (name, description, start_date, end_date, created_by, group_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, name, description, start_date, end_date, created_by, group_id, created_at
    """
    GET_TRIP_BY_ID = """
        SELECT t.*, u.name as creator_name, g.name as group_name
        FROM trips t
        JOIN users u ON t.created_by = u.id
        LEFT JOIN groups g ON t.group_id = g.id
        WHERE t.id = %s AND t.is_active = TRUE
    """
    GET_TRIPS_BY_USER = """
        SELECT t.*, u.name as creator_name, g.name as group_name
        FROM trips t
        JOIN users u ON t.created_by = u.id
        LEFT JOIN groups g ON t.group_id = g.id
        WHERE t.created_by = %s OR t.id IN (
            SELECT trip_id FROM trip_participants WHERE user_id = %s
        )
        ORDER BY t.start_date DESC, t.created_at DESC
    """
    ADD_TRIP_PARTICIPANT = """
        INSERT INTO trip_participants (trip_id, user_id)
        VALUES (%s, %s)
        RETURNING id, trip_id, user_id, joined_at
    """
    GET_TRIP_PARTICIPANTS = """
        SELECT tp.*, u.name, u.email
        FROM trip_participants tp
        JOIN users u ON tp.user_id = u.id
        WHERE tp.trip_id = %s
        ORDER BY tp.joined_at
    """
    NEW_TRIP_EXPENSE = """
        INSERT INTO trip_expenses (trip_id, name, amount, currency, paid_by, description, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, trip_id, name, amount, currency, paid_by, description, date, created_at
    """
    GET_TRIP_EXPENSES = """
        SELECT te.*, u.name as payer_name
        FROM trip_expenses te
        JOIN users u ON te.paid_by = u.id
        WHERE te.trip_id = %s
        ORDER BY te.date DESC, te.created_at DESC
    """
    UPDATE_TRIP = """
        UPDATE trips SET name = %s, description = %s, start_date = %s, end_date = %s
        WHERE id = %s AND created_by = %s RETURNING id
    """
    DELETE_TRIP = "UPDATE trips SET is_active = FALSE WHERE id = %s RETURNING id"


class DB_debt_query(Enum):
    GET_USER_DEBTS = """
        SELECT d.*, 
               u1.name as creditor_name, u1.email as creditor_email,
               u2.name as debtor_name, u2.email as debtor_email
        FROM debts d
        JOIN users u1 ON d.creditor_id = u1.id
        JOIN users u2 ON d.debtor_id = u2.id
        WHERE (d.creditor_id = %s OR d.debtor_id = %s) AND d.is_settled = FALSE
        ORDER BY d.created_at DESC
    """
    GET_DEBTS_BETWEEN_USERS = """
        SELECT d.*, 
               u1.name as creditor_name, u1.email as creditor_email,
               u2.name as debtor_name, u2.email as debtor_email
        FROM debts d
        JOIN users u1 ON d.creditor_id = u1.id
        JOIN users u2 ON d.debtor_id = u2.id
        WHERE ((d.creditor_id = %s AND d.debtor_id = %s) OR 
               (d.creditor_id = %s AND d.debtor_id = %s))
        AND d.is_settled = FALSE
        ORDER BY d.created_at DESC
    """
    SETTLE_DEBT = """
        UPDATE debts SET is_settled = TRUE, settled_at = CURRENT_TIMESTAMP
        WHERE id = %s RETURNING id
    """
    GET_DEBT_SUMMARY = "SELECT * FROM get_user_debts_summary(%s)"


class DB_category_query(Enum):
    GET_ALL_CATEGORIES = """
        SELECT * FROM category 
        ORDER BY is_income DESC, name
    """
    GET_CATEGORIES_BY_TYPE = """
        SELECT * FROM category 
        WHERE is_income = %s
        ORDER BY name
    """
    NEW_CATEGORY = """
        INSERT INTO category (name, is_income, icon, color, parent_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, name, is_income, icon, color, parent_id
    """
    UPDATE_CATEGORY = """
        UPDATE category SET name = %s, is_income = %s, icon = %s, color = %s, parent_id = %s
        WHERE id = %s RETURNING id
    """
    DELETE_CATEGORY = "DELETE FROM category WHERE id = %s RETURNING id"


class DB_budget_query(Enum):
    NEW_BUDGET = """
        INSERT INTO budgets (user_id, group_id, name, amount, period, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, user_id, group_id, name, amount, period, start_date, end_date, created_at
    """
    GET_BUDGETS_BY_USER = """
        SELECT b.*, g.name as group_name
        FROM budgets b
        LEFT JOIN groups g ON b.group_id = g.id
        WHERE b.user_id = %s
        ORDER BY b.start_date DESC, b.created_at DESC
    """
    GET_BUDGET_CATEGORIES = """
        SELECT bc.*, c.name as category_name, c.icon, c.color
        FROM budget_categories bc
        JOIN category c ON bc.category_id = c.id
        WHERE bc.budget_id = %s
        ORDER BY c.name
    """
    ADD_BUDGET_CATEGORY = """
        INSERT INTO budget_categories (budget_id, category_id, planned_amount)
        VALUES (%s, %s, %s)
        RETURNING id, budget_id, category_id, planned_amount, created_at
    """
    UPDATE_BUDGET = """
        UPDATE budgets SET name = %s, amount = %s, period = %s, start_date = %s, end_date = %s
        WHERE id = %s AND user_id = %s RETURNING id
    """
    DELETE_BUDGET = "DELETE FROM budgets WHERE id = %s RETURNING id"


