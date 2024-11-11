CREATE TABLE usuarios (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    user_role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE cards (
    card_id SERIAL PRIMARY KEY,
    user_id INT,
    card_number VARCHAR(16) NOT NULL,
    expiration_date DATE NOT NULL,
    cvv VARCHAR(4) NOT NULL,
    CONSTRAINT fk_user
        FOREIGN KEY(user_id) REFERENCES usuarios(user_id)
        ON DELETE CASCADE
);