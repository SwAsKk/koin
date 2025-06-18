CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS types (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    is_income BOOLEAN NOT NULL DEFAULT true
);


CREATE TABLE IF NOT EXISTS trans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    type_id INTEGER REFERENCES types(id),
    value INTEGER NOT NULL DEFAULT 0,
    description TEXT
);


CREATE TABLE IF NOT EXISTS category (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trans_category (
    id SERIAL PRIMARY KEY,
    trans_id INTEGER NOT NULL REFERENCES trans(id),
    category_id INTEGER NOT NULL REFERENCES category(id)
);
