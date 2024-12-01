CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    address VARCHAR(200) NOT NULL,
    password VARCHAR(200) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'invitado', 'usuario'))
);

CREATE TABLE IF NOT EXISTS purchases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    product_name VARCHAR(100) NOT NULL,
    amount INTEGER NOT NULL
);