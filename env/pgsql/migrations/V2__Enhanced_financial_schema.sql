-- Enhanced Financial Schema for Koin App
-- V2: Adding comprehensive financial management features

-- 1. Enhanced Users table with additional fields
ALTER TABLE users ADD COLUMN IF NOT EXISTS email TEXT UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- 2. Bank Accounts table
CREATE TABLE IF NOT EXISTS bank_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL, -- "Основной счет", "Сбережения", "Кредитная карта"
    account_number TEXT,
    balance DECIMAL(15,2) DEFAULT 0.00,
    currency TEXT DEFAULT 'RUB',
    bank_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Investment Accounts table
CREATE TABLE IF NOT EXISTS investment_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL, -- "Брокерский счет", "ИИС", "Вклад"
    account_type TEXT NOT NULL, -- 'brokerage', 'iis', 'deposit', 'crypto'
    balance DECIMAL(15,2) DEFAULT 0.00,
    currency TEXT DEFAULT 'RUB',
    institution_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Groups table for family/shared expenses
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL, -- "Семья", "Друзья", "Коллеги"
    description TEXT,
    created_by INTEGER NOT NULL REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Group Members table
CREATE TABLE IF NOT EXISTS group_members (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member', -- 'owner', 'admin', 'member'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, user_id)
);

-- 6. Enhanced Categories with hierarchy
ALTER TABLE category ADD COLUMN IF NOT EXISTS parent_id INTEGER REFERENCES category(id);
ALTER TABLE category ADD COLUMN IF NOT EXISTS is_income BOOLEAN DEFAULT FALSE;
ALTER TABLE category ADD COLUMN IF NOT EXISTS icon TEXT;
ALTER TABLE category ADD COLUMN IF NOT EXISTS color TEXT;

-- 7. Enhanced Transactions table
ALTER TABLE trans ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE trans ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE trans ADD COLUMN IF NOT EXISTS is_shared BOOLEAN DEFAULT FALSE;
ALTER TABLE trans ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES groups(id);
ALTER TABLE trans ADD COLUMN IF NOT EXISTS bank_account_id INTEGER REFERENCES bank_accounts(id);
ALTER TABLE trans ADD COLUMN IF NOT EXISTS investment_account_id INTEGER REFERENCES investment_accounts(id);
ALTER TABLE trans ADD COLUMN IF NOT EXISTS date DATE DEFAULT CURRENT_DATE;

-- 8. Trips table
CREATE TABLE IF NOT EXISTS trips (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL, -- "Поездка в Москву", "Отпуск в Турции"
    description TEXT,
    start_date DATE,
    end_date DATE,
    created_by INTEGER NOT NULL REFERENCES users(id),
    group_id INTEGER REFERENCES groups(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Trip Participants table
CREATE TABLE IF NOT EXISTS trip_participants (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(trip_id, user_id)
);

-- 10. Trip Expenses table
CREATE TABLE IF NOT EXISTS trip_expenses (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    name TEXT NOT NULL, -- "Отель", "Билеты", "Еда"
    amount DECIMAL(15,2) NOT NULL,
    currency TEXT DEFAULT 'RUB',
    paid_by INTEGER NOT NULL REFERENCES users(id),
    description TEXT,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Expense Shares table - who owes money for shared expenses
CREATE TABLE IF NOT EXISTS expense_shares (
    id SERIAL PRIMARY KEY,
    expense_id INTEGER NOT NULL, -- can reference either trans.id or trip_expenses.id
    expense_type TEXT NOT NULL, -- 'transaction' or 'trip_expense'
    user_id INTEGER NOT NULL REFERENCES users(id),
    share_amount DECIMAL(15,2) NOT NULL, -- how much this user owes
    share_percentage DECIMAL(5,2), -- percentage of total expense
    is_paid BOOLEAN DEFAULT FALSE,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. Debts table for tracking who owes what to whom
CREATE TABLE IF NOT EXISTS debts (
    id SERIAL PRIMARY KEY,
    creditor_id INTEGER NOT NULL REFERENCES users(id), -- who is owed money
    debtor_id INTEGER NOT NULL REFERENCES users(id), -- who owes money
    amount DECIMAL(15,2) NOT NULL,
    currency TEXT DEFAULT 'RUB',
    description TEXT,
    expense_id INTEGER, -- reference to trans.id or trip_expenses.id
    expense_type TEXT, -- 'transaction' or 'trip_expense'
    is_settled BOOLEAN DEFAULT FALSE,
    settled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Recurring Transactions table
CREATE TABLE IF NOT EXISTS recurring_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    frequency TEXT NOT NULL, -- 'daily', 'weekly', 'monthly', 'yearly'
    start_date DATE NOT NULL,
    end_date DATE,
    category_id INTEGER REFERENCES category(id),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. Budgets table for monthly/yearly planning
CREATE TABLE IF NOT EXISTS budgets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    group_id INTEGER REFERENCES groups(id),
    name TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    period TEXT NOT NULL, -- 'monthly', 'yearly'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. Budget Categories table
CREATE TABLE IF NOT EXISTS budget_categories (
    id SERIAL PRIMARY KEY,
    budget_id INTEGER NOT NULL REFERENCES budgets(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES category(id),
    planned_amount DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_trans_user_id ON trans(user_id);
CREATE INDEX IF NOT EXISTS idx_trans_group_id ON trans(group_id);
CREATE INDEX IF NOT EXISTS idx_trans_date ON trans(date);
CREATE INDEX IF NOT EXISTS idx_trip_expenses_trip_id ON trip_expenses(trip_id);
CREATE INDEX IF NOT EXISTS idx_expense_shares_expense_id ON expense_shares(expense_id);
CREATE INDEX IF NOT EXISTS idx_debts_creditor_debtor ON debts(creditor_id, debtor_id);
CREATE INDEX IF NOT EXISTS idx_group_members_group_id ON group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_bank_accounts_user_id ON bank_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_investment_accounts_user_id ON investment_accounts(user_id);

-- Insert default categories
INSERT INTO category (name, is_income, icon, color) VALUES 
    ('Зарплата', TRUE, '💰', '#28a745'),
    ('Продукты', FALSE, '🛒', '#dc3545'),
    ('Транспорт', FALSE, '🚗', '#007bff'),
    ('Развлечения', FALSE, '🎮', '#6f42c1'),
    ('Здоровье', FALSE, '🏥', '#fd7e14'),
    ('Одежда', FALSE, '👕', '#e83e8c'),
    ('Рестораны', FALSE, '🍽️', '#ffc107'),
    ('Путешествия', FALSE, '✈️', '#17a2b8'),
    ('Инвестиции', TRUE, '📈', '#20c997'),
    ('Проценты по вкладам', TRUE, '🏦', '#28a745')
ON CONFLICT DO NOTHING;

-- Insert default transaction types
INSERT INTO types (name, is_income) VALUES 
    ('Доход', TRUE),
    ('Расход', FALSE),
    ('Перевод', FALSE)
ON CONFLICT DO NOTHING; 