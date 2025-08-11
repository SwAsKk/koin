-- V4: Update existing data and add missing fields

-- Update existing users table to add missing columns
UPDATE users SET 
    email = CONCAT(name, '@example.com'),
    created_at = CURRENT_TIMESTAMP,
    is_active = TRUE
WHERE email IS NULL;

-- Update existing transactions to add missing columns
UPDATE trans SET 
    created_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP,
    is_shared = FALSE,
    date = CURRENT_DATE
WHERE created_at IS NULL;

-- Update existing categories to add missing columns
UPDATE category SET 
    is_income = FALSE,
    icon = '📁',
    color = '#6c757d'
WHERE is_income IS NULL;

-- Set specific categories as income
UPDATE category SET 
    is_income = TRUE,
    icon = '💰',
    color = '#28a745'
WHERE name IN ('Зарплата', 'Инвестиции', 'Проценты по вкладам');

-- Set specific categories as expense with proper icons
UPDATE category SET 
    icon = '🛒',
    color = '#dc3545'
WHERE name = 'Продукты';

UPDATE category SET 
    icon = '🚗',
    color = '#007bff'
WHERE name = 'Транспорт';

UPDATE category SET 
    icon = '🎮',
    color = '#6f42c1'
WHERE name = 'Развлечения';

UPDATE category SET 
    icon = '🏥',
    color = '#fd7e14'
WHERE name = 'Здоровье';

UPDATE category SET 
    icon = '👕',
    color = '#e83e8c'
WHERE name = 'Одежда';

UPDATE category SET 
    icon = '🍽️',
    color = '#ffc107'
WHERE name = 'Рестораны';

UPDATE category SET 
    icon = '✈️',
    color = '#17a2b8'
WHERE name = 'Путешествия';

UPDATE category SET 
    icon = '📈',
    color = '#20c997'
WHERE name = 'Инвестиции';

UPDATE category SET 
    icon = '🏦',
    color = '#28a745'
WHERE name = 'Проценты по вкладам';

-- Create default bank account for existing users
INSERT INTO bank_accounts (user_id, name, account_number, balance, currency, bank_name)
SELECT 
    id,
    'Основной счет',
    CONCAT('ACC-', id),
    0.00,
    'RUB',
    'Основной банк'
FROM users
WHERE id NOT IN (SELECT DISTINCT user_id FROM bank_accounts);

-- Create default investment account for existing users
INSERT INTO investment_accounts (user_id, name, account_type, balance, currency, institution_name)
SELECT 
    id,
    'Основные сбережения',
    'deposit',
    0.00,
    'RUB',
    'Основной банк'
FROM users
WHERE id NOT IN (SELECT DISTINCT user_id FROM investment_accounts);

-- Create default group for existing users (personal group)
INSERT INTO groups (name, description, created_by)
SELECT 
    CONCAT('Личные финансы - ', name),
    'Персональная группа для управления личными финансами',
    id
FROM users
WHERE id NOT IN (SELECT DISTINCT created_by FROM groups);

-- Add users to their personal groups
INSERT INTO group_members (group_id, user_id, role)
SELECT 
    g.id,
    g.created_by,
    'owner'
FROM groups g
WHERE g.id NOT IN (SELECT DISTINCT group_id FROM group_members);

-- Update existing transactions to link with default bank account
UPDATE trans SET 
    bank_account_id = (
        SELECT ba.id 
        FROM bank_accounts ba 
        WHERE ba.user_id = trans.user_id 
        AND ba.name = 'Основной счет'
        LIMIT 1
    )
WHERE bank_account_id IS NULL;

-- Set default transaction type for existing transactions
UPDATE trans SET type_id = 2 WHERE type_id IS NULL; -- Default to expense

-- Add constraints to ensure data integrity
ALTER TABLE trans ALTER COLUMN date SET NOT NULL;
ALTER TABLE trans ALTER COLUMN created_at SET NOT NULL;
ALTER TABLE trans ALTER COLUMN updated_at SET NOT NULL;

-- Add check constraints
ALTER TABLE trans ADD CONSTRAINT check_transaction_value CHECK (value > 0);
ALTER TABLE bank_accounts ADD CONSTRAINT check_bank_balance CHECK (balance >= 0);
ALTER TABLE investment_accounts ADD CONSTRAINT check_investment_balance CHECK (balance >= 0);

-- Add unique constraints
ALTER TABLE users ADD CONSTRAINT unique_user_email UNIQUE (email);
ALTER TABLE group_members ADD CONSTRAINT unique_group_user UNIQUE (group_id, user_id);
ALTER TABLE trip_participants ADD CONSTRAINT unique_trip_user UNIQUE (trip_id, user_id);

-- Create view for easy access to user financial summary
CREATE OR REPLACE VIEW user_financial_summary AS
SELECT 
    u.id as user_id,
    u.name as user_name,
    u.email,
    COALESCE(SUM(ba.balance), 0) as total_bank_balance,
    COALESCE(SUM(ia.balance), 0) as total_investment_balance,
    COALESCE(SUM(ba.balance), 0) + COALESCE(SUM(ia.balance), 0) as total_balance,
    COUNT(DISTINCT ba.id) as bank_accounts_count,
    COUNT(DISTINCT ia.id) as investment_accounts_count
FROM users u
LEFT JOIN bank_accounts ba ON u.id = ba.user_id AND ba.is_active = TRUE
LEFT JOIN investment_accounts ia ON u.id = ia.user_id AND ia.is_active = TRUE
GROUP BY u.id, u.name, u.email;

-- Create view for group financial summary
CREATE OR REPLACE VIEW group_financial_summary AS
SELECT 
    g.id as group_id,
    g.name as group_name,
    g.description,
    COUNT(gm.user_id) as members_count,
    COALESCE(SUM(CASE WHEN t.is_shared = TRUE THEN t.value ELSE 0 END), 0) as total_shared_expenses,
    COALESCE(SUM(CASE WHEN t.is_shared = FALSE THEN t.value ELSE 0 END), 0) as total_personal_expenses
FROM groups g
LEFT JOIN group_members gm ON g.id = gm.group_id
LEFT JOIN trans t ON g.id = t.group_id
WHERE g.is_active = TRUE
GROUP BY g.id, g.name, g.description;

-- Create view for trip financial summary
CREATE OR REPLACE VIEW trip_financial_summary AS
SELECT 
    t.id as trip_id,
    t.name as trip_name,
    t.description,
    t.start_date,
    t.end_date,
    COUNT(tp.user_id) as participants_count,
    COALESCE(SUM(te.amount), 0) as total_expenses,
    COUNT(te.id) as expenses_count
FROM trips t
LEFT JOIN trip_participants tp ON t.id = tp.trip_id
LEFT JOIN trip_expenses te ON t.id = te.trip_id
WHERE t.is_active = TRUE
GROUP BY t.id, t.name, t.description, t.start_date, t.end_date; 