-- Создаем таблицу cpu
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS deal (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    value INTEGER NOT NULL,
    is_equally BOOLEAN,
    timestamp TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS participant (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    deal_id INTEGER NOT NULL,
    value INTEGER
);
