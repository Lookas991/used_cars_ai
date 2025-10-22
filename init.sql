CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    year INT,
    mileage INT,
    predicted_price NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);