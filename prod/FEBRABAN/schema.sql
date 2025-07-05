CREATE TABLE segmentos (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE fornecedores (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    id_segmento INTEGER REFERENCES segmentos(id),
    cnpj VARCHAR(14) UNIQUE NOT NULL
);

CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,  
    nome TEXT NOT NULL,
    preco NUMERIC(10, 2) NOT NULL CHECK (preco > 0),
    id_empresa INTEGER REFERENCES fornecedores(id) ON DELETE CASCADE
);

CREATE TABLE lotes (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(44) UNIQUE NOT NULL, 
    id_produto INTEGER REFERENCES produtos(id),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    recebido TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE estoque (
    id_produto INTEGER PRIMARY KEY REFERENCES produtos(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0)
);

CREATE TABLE transacoes (
    id SERIAL PRIMARY KEY,
    tipo_transacao VARCHAR(10) NOT NULL CHECK (tipo_transacao IN ('checkout', 'entry')),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE itens_transacionados (
    id SERIAL PRIMARY KEY,
    id_transacao INTEGER REFERENCES transacoes(id) ON DELETE CASCADE,
    id_produto INTEGER REFERENCES produtos(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco NUMERIC(10, 2) NOT NULL CHECK (preco > 0)
);

INSERT INTO segmentos (nome) VALUES
  ('Padaria'),
  ('Frios e Laticínios'),
  ('Hortifrúti'),
  ('Limpeza'),
  ('Bebidas Alcoólicas');

INSERT INTO fornecedores (nome, id_segmento, cnpj) VALUES
  ('Panificadora Pão Quente Ltda', 1, '11111111000191'),
  ('Laticínios Vale Verde',        2, '22222222000192'),
  ('Frutas Tropicais Distribuidora', 3, '33333333000193'),
  ('Limpa Fácil Indústria Química', 4, '44444444000194'),
  ('Cervejaria Serra Alta',        5, '55555555000195');

INSERT INTO produtos (codigo, nome, preco, id_empresa) VALUES
  ('7891111000001', 'Pão Francês 1kg',         9.90, 1),
  ('7892222000002', 'Queijo Minas Frescal 500g', 18.50, 2),
  ('7893333000003', 'Banana Nanica 1kg',        4.29, 3),
  ('7894444000004', 'Desinfetante Lavanda 2L',  7.75, 4),
  ('7895555000005', 'Cerveja Pilsen 600ml',     5.20, 5);

INSERT INTO estoque (id_produto, quantidade) VALUES
  (1, 0),
  (2, 0),
  (3, 0),
  (4, 0),
  (5, 0);
