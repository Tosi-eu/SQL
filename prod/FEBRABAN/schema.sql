CREATE TABLE segments (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    segment_id INTEGER REFERENCES segments(id),
    cnpj VARCHAR(14) UNIQUE NOT NULL
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,  
    name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE
);

CREATE TABLE lots (
    id SERIAL PRIMARY KEY,
    lot_code VARCHAR(44) UNIQUE NOT NULL, 
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE stock (
    product_id INTEGER PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0)
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('checkout', 'entry')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transaction_items (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0)
);

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    changed_data JSONB NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dados iniciais
INSERT INTO segments (name) VALUES
  ('Alimentos'),
  ('Bebidas'),
  ('Higiene'),
  ('Limpeza'),
  ('Petshop');

INSERT INTO companies (name, segment_id, cnpj) VALUES
  ('Nestlé Brasil Ltda',        1, '02345678000190'),
  ('Coca-Cola Indústrias',      2, '04567891000180'),
  ('Unilever Higiene',          3, '06789123000170'),
  ('Procter & Gamble',          4, '08912345000160'),
  ('Purina Petcare',            5, '02402002000134');       

INSERT INTO products (code, name, price, company_id) VALUES
  ('7891000050001', 'Leite Condensado Nestlé 395g', 6.99, 1),
  ('7894900010015', 'Coca-Cola 2L', 8.49, 2),
  ('7891150020020', 'Sabonete Dove 90g', 3.79, 3),
  ('7891234567890', 'Detergente Ariel 500ml', 4.50, 4),
  ('7896066339015', 'Ração Purina 1kg', 15.90, 5);

INSERT INTO stock (product_id, quantity) VALUES
  (1, 0),
  (2, 0),
  (3, 0),
  (4, 0),
  (5, 0);