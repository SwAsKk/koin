# 🏦 Схема базы данных Koin - Финансовое приложение

## 📋 Обзор

Koin - это приложение для учета личных и общих финансов с поддержкой поездок, групп и автоматического расчета долгов.

## 🗄️ Основные таблицы

### 👥 Users (Пользователи)
```sql
users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
)
```

### 🏦 Bank Accounts (Банковские счета)
```sql
bank_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name TEXT NOT NULL, -- "Основной счет", "Сбережения", "Кредитная карта"
    account_number TEXT,
    balance DECIMAL(15,2) DEFAULT 0.00,
    currency TEXT DEFAULT 'RUB',
    bank_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 📈 Investment Accounts (Инвестиционные счета)
```sql
investment_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name TEXT NOT NULL, -- "Брокерский счет", "ИИС", "Вклад"
    account_type TEXT NOT NULL, -- 'brokerage', 'iis', 'deposit', 'crypto'
    balance DECIMAL(15,2) DEFAULT 0.00,
    currency TEXT DEFAULT 'RUB',
    institution_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 👨‍👩‍👧‍👦 Groups (Группы)
```sql
groups (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL, -- "Семья", "Друзья", "Коллеги"
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 🔗 Group Members (Участники групп)
```sql
group_members (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups(id),
    user_id INTEGER REFERENCES users(id),
    role TEXT DEFAULT 'member', -- 'owner', 'admin', 'member'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 💰 Transactions (Транзакции)
```sql
trans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name TEXT NOT NULL,
    type_id INTEGER REFERENCES types(id),
    value INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_shared BOOLEAN DEFAULT FALSE,
    group_id INTEGER REFERENCES groups(id),
    bank_account_id INTEGER REFERENCES bank_accounts(id),
    investment_account_id INTEGER REFERENCES investment_accounts(id),
    date DATE DEFAULT CURRENT_DATE
)
```

### ✈️ Trips (Поездки)
```sql
trips (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL, -- "Поездка в Москву", "Отпуск в Турции"
    description TEXT,
    start_date DATE,
    end_date DATE,
    created_by INTEGER REFERENCES users(id),
    group_id INTEGER REFERENCES groups(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 🎫 Trip Participants (Участники поездки)
```sql
trip_participants (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER REFERENCES trips(id),
    user_id INTEGER REFERENCES users(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 💸 Trip Expenses (Траты в поездках)
```sql
trip_expenses (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER REFERENCES trips(id),
    name TEXT NOT NULL, -- "Отель", "Билеты", "Еда"
    amount DECIMAL(15,2) NOT NULL,
    currency TEXT DEFAULT 'RUB',
    paid_by INTEGER REFERENCES users(id),
    description TEXT,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 📊 Expense Shares (Доли в тратах)
```sql
expense_shares (
    id SERIAL PRIMARY KEY,
    expense_id INTEGER NOT NULL, -- ссылка на trans.id или trip_expenses.id
    expense_type TEXT NOT NULL, -- 'transaction' или 'trip_expense'
    user_id INTEGER REFERENCES users(id),
    share_amount DECIMAL(15,2) NOT NULL, -- сколько должен этот пользователь
    share_percentage DECIMAL(5,2), -- процент от общей суммы
    is_paid BOOLEAN DEFAULT FALSE,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 💳 Debts (Долги)
```sql
debts (
    id SERIAL PRIMARY KEY,
    creditor_id INTEGER REFERENCES users(id), -- кому должны
    debtor_id INTEGER REFERENCES users(id), -- кто должен
    amount DECIMAL(15,2) NOT NULL,
    currency TEXT DEFAULT 'RUB',
    description TEXT,
    expense_id INTEGER, -- ссылка на trans.id или trip_expenses.id
    expense_type TEXT, -- 'transaction' или 'trip_expense'
    is_settled BOOLEAN DEFAULT FALSE,
    settled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 🔄 Recurring Transactions (Повторяющиеся транзакции)
```sql
recurring_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    frequency TEXT NOT NULL, -- 'daily', 'weekly', 'monthly', 'yearly'
    start_date DATE NOT NULL,
    end_date DATE,
    category_id INTEGER REFERENCES category(id),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 📅 Budgets (Бюджеты)
```sql
budgets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    group_id INTEGER REFERENCES groups(id),
    name TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    period TEXT NOT NULL, -- 'monthly', 'yearly'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 📊 Budget Categories (Категории бюджета)
```sql
budget_categories (
    id SERIAL PRIMARY KEY,
    budget_id INTEGER REFERENCES budgets(id),
    category_id INTEGER REFERENCES category(id),
    planned_amount DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## 🔧 Автоматические функции

### 💰 Обновление балансов
- При создании/изменении/удалении транзакций автоматически обновляются балансы банковских и инвестиционных счетов
- Поддерживаются доходы, расходы и переводы

### 🏦 Создание долгов
- При создании общей траты (`is_shared = TRUE`) автоматически создаются записи долгов для всех участников группы
- При создании траты в поездке автоматически создаются долги для всех участников поездки
- Долги рассчитываются поровну между всеми участниками

### 📊 Представления (Views)
- `user_financial_summary` - сводка по финансам пользователя
- `group_financial_summary` - сводка по финансам группы
- `trip_financial_summary` - сводка по финансам поездки

## 🚀 Как это работает

### 1. **Личные траты**
- Пользователь создает транзакцию с `is_shared = FALSE`
- Трата привязывается к конкретному банковскому счету
- Баланс счета автоматически обновляется

### 2. **Общие траты**
- Пользователь создает транзакцию с `is_shared = TRUE` и указывает `group_id`
- Система автоматически создает долги для всех участников группы
- Каждый участник получает уведомление о своем долге

### 3. **Поездки**
- Создается поездка с участниками
- При добавлении траты указывается, кто оплатил
- Система автоматически рассчитывает долги для всех участников
- Долги отображаются в отдельной таблице

### 4. **Управление долгами**
- Пользователь видит все свои долги и кто ему должен
- При погашении долга обновляется статус
- История всех операций сохраняется

## 📱 API Endpoints (планируется)

- `POST /api/groups` - создание группы
- `POST /api/groups/{id}/members` - добавление участника в группу
- `POST /api/trips` - создание поездки
- `POST /api/trips/{id}/expenses` - добавление траты в поездку
- `GET /api/users/{id}/debts` - получение долгов пользователя
- `POST /api/debts/{id}/settle` - погашение долга

## 🔒 Безопасность

- Все таблицы имеют ограничения целостности
- Проверки на положительные значения для сумм
- Уникальные ограничения для предотвращения дублирования
- Каскадное удаление для связанных записей

## 📈 Производительность

- Созданы индексы для часто используемых полей
- Представления для быстрого доступа к сводкам
- Триггеры для автоматического обновления связанных данных 