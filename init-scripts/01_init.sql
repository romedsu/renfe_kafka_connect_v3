-- CREATE TABLE IF NOT EXISTS transacciones (
--     id SERIAL PRIMARY KEY,
--     usuario_id INT NOT NULL,
--     monto DECIMAL(12, 2) NOT NULL,
--     moneda VARCHAR(3) DEFAULT 'EUR',
--     fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

CREATE TABLE IF NOT EXISTS rutasAenaAsturias (
    id SERIAL PRIMARY KEY,
    destino VARCHAR NOT NULL,
    pais VARCHAR NOT NULL,
    aerolinea VARCHAR NOT NULL
);