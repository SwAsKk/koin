# 📚 API Документация Koin

## 🚀 Обзор

Koin - это финансовое приложение для учета личных и общих трат с поддержкой поездок, групп и автоматического расчета долгов.

**Базовый URL:** `http://localhost:8000`  
**API Base:** `/api`  
**Документация:** `/docs` (Swagger UI) или `/redoc` (ReDoc)

## 🔐 Аутентификация

> **Примечание:** В текущей версии аутентификация не реализована. Все endpoints принимают `user_id` как параметр для демонстрации.

## 👥 Пользователи

### Создать пользователя
```http
POST /user
```

**Тело запроса:**
```json
{
    "name": "Иван Иванов",
    "email": "ivan@example.com",
    "password": "secure_password"
}
```

**Ответ:**
```json
{
    "id": 1
}
```

## 💰 Транзакции

### Создать транзакцию
```http
POST /api/transactions
```

**Тело запроса:**
```json
{
    "user_id": 1,
    "name": "Продукты в магазине",
    "type_id": 2,
    "value": 1500.50,
    "description": "Покупка продуктов на неделю",
    "is_shared": false,
    "group_id": null,
    "bank_account_id": 1,
    "investment_account_id": null,
    "date": "2024-01-15"
}
```

### Получить транзакции пользователя
```http
GET /api/transactions/user/{user_id}
```

### Удалить транзакцию
```http
DELETE /api/transactions/{trans_id}
```

## 👨‍👩‍👧‍👦 Группы

### Создать группу
```http
POST /api/groups
```

**Тело запроса:**
```json
{
    "name": "Семья",
    "description": "Общие траты семьи"
}
```

**Параметры запроса:**
- `user_id` (query): ID пользователя, создающего группу

### Получить группы пользователя
```http
GET /api/groups?user_id={user_id}
```

### Получить информацию о группе
```http
GET /api/groups/{group_id}?user_id={user_id}
```

### Добавить участника в группу
```http
POST /api/groups/{group_id}/members?user_id={user_id}
```

**Тело запроса:**
```json
{
    "user_id": 2,
    "role": "member"
}
```

### Обновить группу
```http
PUT /api/groups/{group_id}?user_id={user_id}
```

**Тело запроса:**
```json
{
    "name": "Семья Ивановых",
    "description": "Обновленное описание"
}
```

### Удалить группу
```http
DELETE /api/groups/{group_id}?user_id={user_id}
```

## ✈️ Поездки

### Создать поездку
```http
POST /api/trips
```

**Тело запроса:**
```json
{
    "name": "Отпуск в Турции",
    "description": "Летний отпуск на море",
    "start_date": "2024-07-01",
    "end_date": "2024-07-15",
    "group_id": 1
}
```

**Параметры запроса:**
- `user_id` (query): ID пользователя, создающего поездку

### Получить поездки пользователя
```http
GET /api/trips?user_id={user_id}
```

### Получить информацию о поездке
```http
GET /api/trips/{trip_id}?user_id={user_id}
```

### Добавить участника в поездку
```http
POST /api/trips/{trip_id}/participants?user_id={user_id}
```

**Тело запроса:**
```json
{
    "user_id": 2
}
```

### Добавить трату в поездку
```http
POST /api/trips/{trip_id}/expenses?user_id={user_id}
```

**Тело запроса:**
```json
{
    "name": "Отель",
    "amount": 50000.00,
    "currency": "RUB",
    "description": "Проживание в отеле",
    "date": "2024-07-01"
}
```

### Получить траты поездки
```http
GET /api/trips/{trip_id}/expenses?user_id={user_id}
```

### Обновить поездку
```http
PUT /api/trips/{trip_id}?user_id={user_id}
```

### Удалить поездку
```http
DELETE /api/trips/{trip_id}?user_id={user_id}
```

## 💳 Долги

### Получить долги пользователя
```http
GET /api/debts?user_id={user_id}
```

### Получить сводку по долгам
```http
GET /api/debts/summary?user_id={user_id}
```

**Ответ:**
```json
{
    "owes_total": 2500.00,
    "owed_total": 1500.00,
    "net_balance": -1000.00
}
```

### Получить долги между пользователями
```http
GET /api/debts/between/{other_user_id}?user_id={user_id}
```

### Погасить долг
```http
POST /api/debts/{debt_id}/settle?user_id={user_id}
```

### Получить долги в группе
```http
GET /api/debts/group/{group_id}?user_id={user_id}
```

### Получить долги в поездке
```http
GET /api/debts/trip/{trip_id}?user_id={user_id}
```

## 🏦 Банковские счета

### Создать банковский счет
```http
POST /api/bank-accounts
```

**Тело запроса:**
```json
{
    "name": "Основной счет",
    "account_number": "1234567890",
    "balance": 100000.00,
    "currency": "RUB",
    "bank_name": "Сбербанк"
}
```

**Параметры запроса:**
- `user_id` (query): ID пользователя

### Получить банковские счета пользователя
```http
GET /api/bank-accounts?user_id={user_id}
```

### Получить информацию о счете
```http
GET /api/bank-accounts/{account_id}?user_id={user_id}
```

### Обновить банковский счет
```http
PUT /api/bank-accounts/{account_id}?user_id={user_id}
```

### Удалить банковский счет
```http
DELETE /api/bank-accounts/{account_id}?user_id={user_id}
```

### Получить баланс счета
```http
GET /api/bank-accounts/{account_id}/balance?user_id={user_id}
```

### Получить сводку по счетам
```http
GET /api/bank-accounts/summary?user_id={user_id}
```

## 📊 Категории

### Получить все категории
```http
GET /api/categories
```

### Получить категории по типу
```http
GET /api/categories?is_income={true|false}
```

### Создать категорию
```http
POST /api/categories
```

**Тело запроса:**
```json
{
    "name": "Новая категория",
    "is_income": false,
    "icon": "🎯",
    "color": "#ff6b6b",
    "parent_id": null
}
```

## 📅 Бюджеты

### Создать бюджет
```http
POST /api/budgets
```

**Тело запроса:**
```json
{
    "name": "Месячный бюджет",
    "amount": 50000.00,
    "period": "monthly",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "group_id": null
}
```

### Получить бюджеты пользователя
```http
GET /api/budgets?user_id={user_id}
```

### Получить категории бюджета
```http
GET /api/budgets/{budget_id}/categories
```

### Добавить категорию в бюджет
```http
POST /api/budgets/{budget_id}/categories
```

**Тело запроса:**
```json
{
    "category_id": 1,
    "planned_amount": 10000.00
}
```

## 🔧 Системные endpoints

### Проверка здоровья
```http
GET /health
```

**Ответ:**
```json
{
    "status": "healthy",
    "database": "connected"
}
```

### Корневой endpoint
```http
GET /
```

**Ответ:**
```json
{
    "message": "Добро пожаловать в Koin - Финансовое приложение!",
    "version": "2.0.0",
    "docs": "/docs",
    "redoc": "/redoc"
}
```

## 📝 Примеры использования

### Создание общей траты в группе

1. **Создать группу:**
```http
POST /api/groups?user_id=1
{
    "name": "Семья",
    "description": "Общие траты"
}
```

2. **Добавить участников:**
```http
POST /api/groups/1/members?user_id=1
{
    "user_id": 2,
    "role": "member"
}
```

3. **Создать общую трату:**
```http
POST /api/transactions
{
    "user_id": 1,
    "name": "Продукты для семьи",
    "type_id": 2,
    "value": 3000.00,
    "description": "Продукты на неделю",
    "is_shared": true,
    "group_id": 1,
    "bank_account_id": 1,
    "date": "2024-01-15"
}
```

4. **Автоматически создаются долги:**
```http
GET /api/debts?user_id=2
```

### Создание поездки с тратами

1. **Создать поездку:**
```http
POST /api/trips?user_id=1
{
    "name": "Поездка в Москву",
    "description": "Деловая поездка",
    "start_date": "2024-02-01",
    "end_date": "2024-02-03"
}
```

2. **Добавить участников:**
```http
POST /api/trips/1/participants?user_id=1
{
    "user_id": 2
}
```

3. **Добавить трату:**
```http
POST /api/trips/1/expenses?user_id=1
{
    "name": "Отель",
    "amount": 15000.00,
    "description": "Проживание"
}
```

4. **Просмотреть долги:**
```http
GET /api/debts/trip/1?user_id=2
```

## ⚠️ Важные замечания

1. **Аутентификация:** В текущей версии не реализована. Все endpoints принимают `user_id` как параметр.
2. **Валидация:** Все данные валидируются через Pydantic модели.
3. **Транзакции:** База данных автоматически обновляет балансы и создает долги.
4. **Права доступа:** Проверяются права пользователя на доступ к ресурсам.
5. **Обработка ошибок:** Все ошибки возвращаются в стандартном формате с HTTP кодами.

## 🚀 Следующие шаги

1. **Аутентификация:** Добавить JWT токены
2. **Авторизация:** Система ролей и разрешений
3. **Уведомления:** Уведомления о новых долгах
4. **Отчеты:** Финансовая аналитика и отчеты
5. **Мобильное приложение:** React Native или Flutter 