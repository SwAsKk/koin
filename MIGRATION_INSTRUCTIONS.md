# 📋 Инструкции по применению миграций

## 🚀 Применение новых миграций

### 1. **Остановите приложение**
```bash
docker-compose down
```

### 2. **Примените миграции**
```bash
# Запустите только базу данных
docker-compose up db -d

# Дождитесь, пока база данных полностью запустится
docker-compose logs db

# Примените миграции через Flyway
docker-compose --profile cli-flyway run --rm cli-flyway migrate
```

### 3. **Проверьте статус миграций**
```bash
docker-compose --profile cli-flyway run --rm cli-flyway info
```

### 4. **Запустите приложение**
```bash
docker-compose up -d
```

## 📊 Что изменилось в базе данных

### **Новые таблицы:**
- `bank_accounts` - банковские счета пользователей
- `investment_accounts` - инвестиционные счета
- `groups` - группы для общих трат
- `group_members` - участники групп
- `trips` - поездки
- `trip_participants` - участники поездок
- `trip_expenses` - траты в поездках
- `expense_shares` - доли в тратах
- `debts` - долги между пользователями
- `recurring_transactions` - повторяющиеся транзакции
- `budgets` - бюджеты
- `budget_categories` - категории бюджетов

### **Расширенные таблицы:**
- `users` - добавлены email, created_at, is_active
- `trans` - добавлены is_shared, group_id, bank_account_id, investment_account_id, date
- `category` - добавлены is_income, icon, color, parent_id

### **Автоматические функции:**
- Обновление балансов банковских и инвестиционных счетов
- Автоматическое создание долгов для общих трат
- Автоматическое создание долгов для трат в поездках
- Представления для быстрого доступа к финансовым сводкам

## ⚠️ Важные замечания

### **Перед применением миграций:**
1. Сделайте резервную копию базы данных
2. Убедитесь, что у вас есть права на создание функций и триггеров
3. Проверьте, что PostgreSQL версии 12+ (для поддержки `IF NOT EXISTS`)

### **После применения миграций:**
1. Проверьте, что все таблицы созданы корректно
2. Убедитесь, что триггеры работают
3. Проверьте представления (views)

## 🔍 Проверка корректности миграций

### **Проверка таблиц:**
```sql
-- Подключитесь к базе данных
\c koin

-- Проверьте список таблиц
\dt

-- Проверьте структуру основных таблиц
\d users
\d bank_accounts
\d groups
\d trips
\d debts
```

### **Проверка функций:**
```sql
-- Проверьте список функций
\df

-- Проверьте триггеры
\dt+
```

### **Проверка представлений:**
```sql
-- Проверьте представления
\dv

-- Проверьте данные в представлениях
SELECT * FROM user_financial_summary LIMIT 5;
SELECT * FROM group_financial_summary LIMIT 5;
SELECT * FROM trip_financial_summary LIMIT 5;
```

## 🚨 Возможные проблемы и решения

### **Ошибка "function already exists"**
```sql
-- Удалите существующую функцию
DROP FUNCTION IF EXISTS function_name CASCADE;
-- Затем примените миграцию заново
```

### **Ошибка "trigger already exists"**
```sql
-- Удалите существующий триггер
DROP TRIGGER IF EXISTS trigger_name ON table_name;
-- Затем примените миграцию заново
```

### **Ошибка "constraint already exists"**
```sql
-- Удалите существующее ограничение
ALTER TABLE table_name DROP CONSTRAINT IF EXISTS constraint_name;
-- Затем примените миграцию заново
```

## 📞 Поддержка

Если возникли проблемы с применением миграций:
1. Проверьте логи Flyway: `docker-compose logs cli-flyway`
2. Проверьте логи базы данных: `docker-compose logs db`
3. Убедитесь, что все файлы миграций находятся в правильной папке
4. Проверьте права доступа к базе данных 