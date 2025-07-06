CREATE TABLE segments (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    cnpj VARCHAR(14) UNIQUE NOT NULL
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE product_supplier (
    id SERIAL PRIMARY KEY,
    code VARCHAR(13) NOT NULL,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE CASCADE,
    segment_id INTEGER REFERENCES segments(id),
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    UNIQUE(product_id, supplier_id),
    UNIQUE(code)
);

CREATE TABLE stock (
    product_id INTEGER PRIMARY KEY REFERENCES product_supplier(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0)
);

CREATE TABLE lots (
    id SERIAL PRIMARY KEY,
    code VARCHAR(44) UNIQUE NOT NULL,
    product_id INTEGER REFERENCES product_supplier(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    validity DATE NOT NULL,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('checkout', 'entry')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transaction_items (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES product_supplier(id) ON DELETE CASCADE,
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

-- Segments
INSERT INTO segments (name) VALUES
  ('Bakery'),
  ('Dairy and Cold Cuts'),
  ('Produce'),
  ('Cleaning'),
  ('Alcoholic Beverages');

-- Suppliers
INSERT INTO suppliers (name, cnpj) VALUES
  ('Hot Bread Bakery Ltd.', '11111111000191'),
  ('Green Valley Dairy', '22222222000192'),
  ('Tropical Fruit Distributor', '33333333000193'),
  ('EasyClean Chemical Industry', '44444444000194'),
  ('Serra Alta Brewery', '55555555000195');

-- Products
INSERT INTO products (name) VALUES
  ('French Bread 1kg'),
  ('Fresh Minas Cheese 500g'),
  ('Banana 1kg'),
  ('Lavender Disinfectant 2L'),
  ('Pilsner Beer 600ml');

-- Product-supplier relationships
INSERT INTO product_supplier (code, product_id, supplier_id, segment_id, price) VALUES
  ('PROD001001001', 1, 1, 1, 9.90),
  ('PROD002002002', 2, 2, 2, 18.50),
  ('PROD003003003', 3, 3, 3, 4.29),
  ('PROD004004004', 4, 4, 4, 7.75),
  ('PROD005005005', 5, 5, 5, 5.20);


-- Initial stock
INSERT INTO stock (product_id, quantity) VALUES
  (1, 10),
  (2, 15),
  (3, 20),
  (4, 5),
  (5, 12);
