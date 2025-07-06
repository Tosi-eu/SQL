CREATE TABLE segmentos (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE fornecedores (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    cnpj VARCHAR(14) UNIQUE NOT NULL
);

CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL
);

CREATE TABLE produto_empresa (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(13),
    id_produto INTEGER REFERENCES produtos(id) ON DELETE CASCADE,
    id_empresa INTEGER REFERENCES fornecedores(id) ON DELETE CASCADE,
    id_segmento INTEGER REFERENCES segmentos(id),
    preco NUMERIC(10, 2) NOT NULL CHECK (preco > 0),
    UNIQUE(id_produto, id_empresa),
    UNIQUE(codigo)
);

CREATE TABLE estoque (
    id_produto INTEGER PRIMARY KEY REFERENCES produto_empresa(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0)
);

CREATE TABLE lotes (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(44) UNIQUE NOT NULL,
    id_produto INTEGER REFERENCES produto_empresa(id),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    recebido TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transacoes (
    id SERIAL PRIMARY KEY,
    tipo_transacao VARCHAR(10) NOT NULL CHECK (tipo_transacao IN ('checkout', 'entry')),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE itens_transacionados (
    id SERIAL PRIMARY KEY,
    id_transacao INTEGER REFERENCES transacoes(id) ON DELETE CASCADE,
    id_produto_empresa INTEGER REFERENCES produto_empresa(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco NUMERIC(10, 2) NOT NULL CHECK (preco > 0)
);

-- Segmentos
INSERT INTO segmentos (nome) VALUES
  ('Padaria'),
  ('Frios e Laticínios'),
  ('Hortifrúti'),
  ('Limpeza'),
  ('Bebidas Alcoólicas');

-- Empresas
INSERT INTO fornecedores (nome, cnpj) VALUES
  ('Panificadora Pão Quente Ltda', '11111111000191'),
  ('Laticínios Vale Verde', '22222222000192'),
  ('Frutas Tropicais Distribuidora', '33333333000193'),
  ('Limpa Fácil Indústria Química', '44444444000194'),
  ('Cervejaria Serra Alta', '55555555000195');

-- Produtos genéricos
INSERT INTO produtos (nome) VALUES
  ('Pão Francês 1kg'),
  ('Queijo Minas Frescal 500g'),
  ('Banana Nanica 1kg'),
  ('Desinfetante Lavanda 2L'),
  ('Cerveja Pilsen 600ml');

-- Relações produto-empresa
INSERT INTO produto_empresa (id_produto, id_empresa, id_segmento, preco) VALUES
  (1, 1, 1, 9.90),
  (2, 2, 2, 18.50),
  (3, 3, 3, 4.29),
  (4, 4, 4, 7.75),
  (5, 5, 5, 5.20);

-- Estoque inicial
INSERT INTO estoque (id_produto, quantidade) VALUES
  (1, 10),
  (2, 15),
  (3, 20),
  (4, 5),
  (5, 12);