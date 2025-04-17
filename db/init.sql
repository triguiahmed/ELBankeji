-- init.sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rib BIGINT NOT NULL UNIQUE,  
    email VARCHAR(100) NOT NULL UNIQUE, 
    phone VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    balance FLOAT NOT NULL,
    owner VARCHAR(100) NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    emitter VARCHAR(100) NOT NULL,
    receiver VARCHAR(100) NOT NULL,
    amount FLOAT NOT NULL 
);

CREATE TABLE IF NOT EXISTS loans (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    amount FLOAT NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('pending', 'rejected', 'accepted'))
);

-- Insert fake data (use ON CONFLICT only for columns with UNIQUE constraints)
INSERT INTO users (name, rib, email, phone)
VALUES 
    ('John Doe', 123456789012, 'john.doe@example.com', '+1234567890'),
    ('Jane Smith', 987654321098, 'jane.smith@example.com', '+0987654321')
ON CONFLICT (email) DO NOTHING;

INSERT INTO accounts (balance, owner)
VALUES 
    (1000.0, 'John Doe'),
    (500.0, 'Jane Smith')
ON CONFLICT (id) DO NOTHING;

INSERT INTO loans (user_name, amount, status)
VALUES 
    ('John Doe', 2000.0, 'pending'),
    ('Jane Smith', 1500.0, 'accepted')
ON CONFLICT (id) DO NOTHING;

INSERT INTO transactions (emitter, receiver, amount)
VALUES 
    ('John Doe', 'Jane Smith', 150.50),
    ('Jane Smith', 'John Doe', 200.75);