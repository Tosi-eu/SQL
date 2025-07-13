-- Criação de tabelas
CREATE TABLE segmentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE fornecedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    cnpj VARCHAR(14) NOT NULL UNIQUE
);

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL
);

CREATE TABLE produto_empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(13) UNIQUE,
    id_produto INT NOT NULL,
    id_empresa INT NOT NULL,
    id_segmento INT NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    UNIQUE (id_produt o, id_empresa),
    FOREIGN KEY (id_produto) REFERENCES produtos(id) ON DELETE CASCADE,
    FOREIGN KEY (id_empresa) REFERENCES fornecedores(id) ON DELETE CASCADE,
    FOREIGN KEY (id_segmento) REFERENCES segmentos(id)
);

CREATE TABLE lotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(44) NOT NULL UNIQUE,
    id_produto INT,
    quantidade INT NOT NULL,
    validade DATE NOT NULL,
    recebido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_produto) REFERENCES produto_empresa(id)
);

CREATE TABLE transacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_transacao ENUM('checkout_produtos', 'recebimento_lote') NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE itens_transacionados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_transacao INT NOT NULL,
    id_produto_empresa INT NOT NULL,
    quantidade INT NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_produto_empresa) REFERENCES produto_empresa(id) ON DELETE CASCADE
);

-- Segmentos
INSERT INTO segmentos (nome) VALUES
  ('Padaria'),
  ('Frios e Laticínios'),
  ('Hortifrúti'),
  ('Limpeza'),
  ('Bebidas Alcoólicas');

-- Fornecedores
INSERT INTO fornecedores (nome, cnpj) VALUES
  ('Panificadora Pão Quente Ltda', '11111111000191'),
  ('Laticínios Vale Verde', '22222222000192'),
  ('Frutas Tropicais Distribuidora', '33333333000193'),
  ('Limpa Fácil Indústria Química', '44444444000194'),
  ('Cervejaria Serra Alta', '55555555000195');

-- Produtos
INSERT INTO produtos (nome) VALUES
  ('Pão Francês 1kg'),
  ('Queijo Minas Frescal 500g'),
  ('Banana Nanica 1kg'),
  ('Desinfetante Lavanda 2L'),
  ('Cerveja Pilsen 600ml');

-- Produto-Empresa
INSERT INTO produto_empresa (id_produto, id_empresa, id_segmento, preco) VALUES
  (1, 1, 1, 9.90),
  (2, 2, 2, 18.50),
  (3, 3, 3, 4.29),
  (4, 4, 4, 7.75),
  (5, 5, 5, 5.20);