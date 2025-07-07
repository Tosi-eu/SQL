CREATE TABLE segments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    cnpj VARCHAR(14) UNIQUE NOT NULL
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE product_supplier (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(13) NOT NULL UNIQUE,
    product_id INT,
    supplier_id INT,
    segment_id INT,
    price DECIMAL(10, 2) NOT NULL,
    UNIQUE(product_id, supplier_id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE,
    FOREIGN KEY (segment_id) REFERENCES segments(id),
    CHECK (price > 0)
);

CREATE TABLE stock (
    product_id INT,
    validity DATE,
    quantity INT NOT NULL DEFAULT 0,
    PRIMARY KEY (product_id, validity),
    FOREIGN KEY (product_id) REFERENCES product_supplier(id) ON DELETE CASCADE,
    CHECK (quantity >= 0)
);

CREATE TABLE lots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(44) UNIQUE NOT NULL,
    product_id INT,
    quantity INT NOT NULL,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES product_supplier(id),
    CHECK (quantity > 0)
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_type ENUM('checkout', 'entry') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transaction_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT,
    product_id INT,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product_supplier(id) ON DELETE CASCADE,
    CHECK (quantity > 0),
    CHECK (price > 0)
);

CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    operation ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    changed_data JSON NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dados iniciais
INSERT INTO segments (name) VALUES
  ('Bakery'),
  ('Dairy and Cold Cuts'),
  ('Produce'),
  ('Cleaning'),
  ('Alcoholic Beverages');

INSERT INTO suppliers (name, cnpj) VALUES
  ('Hot Bread Bakery Ltd.', '11111111000191'),
  ('Green Valley Dairy', '22222222000192'),
  ('Tropical Fruit Distributor', '33333333000193'),
  ('EasyClean Chemical Industry', '44444444000194'),
  ('Serra Alta Brewery', '55555555000195');

INSERT INTO products (name) VALUES
  ('French Bread 1kg'),
  ('Fresh Minas Cheese 500g'),
  ('Banana 1kg'),
  ('Lavender Disinfectant 2L'),
  ('Pilsner Beer 600ml');

INSERT INTO product_supplier (code, product_id, supplier_id, segment_id, price) VALUES
  ('PROD001001001', 1, 1, 1, 9.90),
  ('PROD002002002', 2, 2, 2, 18.50),
  ('PROD003003003', 3, 3, 3, 4.29),
  ('PROD004004004', 4, 4, 4, 7.75),
  ('PROD005005005', 5, 5, 5, 5.20);

INSERT INTO stock (product_id, quantity, validity) VALUES
  (1, 10, '2025-12-31'),
  (2, 15, '2025-12-30'),
  (3, 20, '2025-12-29'),
  (4, 5, '2025-12-28'),
  (5, 12, '2025-12-27');
