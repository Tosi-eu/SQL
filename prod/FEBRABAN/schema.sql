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
    lot_code VARCHAR(30) UNIQUE NOT NULL, 
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

CREATE OR REPLACE FUNCTION update_stock_on_transaction() RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT transaction_type FROM transactions WHERE id = NEW.transaction_id) = 'entry' THEN
        UPDATE stock SET quantity = quantity + NEW.quantity WHERE product_id = NEW.product_id;
    ELSE
        UPDATE stock SET quantity = quantity - NEW.quantity WHERE product_id = NEW.product_id;
        IF (SELECT quantity FROM stock WHERE product_id = NEW.product_id) < 0 THEN
            RAISE EXCEPTION 'Estoque insuficiente para o produto ID %', NEW.product_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_stock
AFTER INSERT ON transaction_items
FOR EACH ROW EXECUTE FUNCTION update_stock_on_transaction();

CREATE INDEX idx_products_code ON products(code);

CREATE OR REPLACE FUNCTION audit_trigger_func() RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log(table_name, operation, changed_data)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD));
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log(table_name, operation, changed_data)
        VALUES (TG_TABLE_NAME, TG_OP, json_build_object('old', row_to_json(OLD), 'new', row_to_json(NEW)));
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log(table_name, operation, changed_data)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION validar_data_vencimento_lote() RETURNS TRIGGER AS $$
DECLARE
    data_cod_barras DATE;
BEGIN
    -- Extrai os primeiros 8 dígitos do campo livre (posições 24–31 no código de 44 dígitos)
    -- Campo 24–31 → posição 23–31 (base 0)
    data_cod_barras := TO_DATE(SUBSTRING(NEW.lot_code FROM 24 FOR 8), 'YYYYMMDD');

    IF data_cod_barras < CURRENT_DATE THEN
        RAISE EXCEPTION 'Lote com data vencida (%). Cadastro não permitido.', data_cod_barras;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_data_lote
BEFORE INSERT ON lots
FOR EACH ROW
EXECUTE FUNCTION validar_data_vencimento_lote();

CREATE TRIGGER trg_audit_products
AFTER INSERT OR UPDATE OR DELETE ON products
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER trg_audit_products
AFTER INSERT OR UPDATE OR DELETE ON lots
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER trg_audit_stock
AFTER INSERT OR UPDATE OR DELETE ON stock
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER trg_audit_transactions
AFTER INSERT OR UPDATE OR DELETE ON transactions
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER trg_audit_transaction_items
AFTER INSERT OR UPDATE OR DELETE ON transaction_items
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

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
  (1, 0),  -- Leite Condensado
  (2, 0),  -- Coca-Cola
  (3, 0),  -- Sabonete Dove
  (4, 0),  -- Detergente Ariel
  (5, 0);  -- Ração Purina

