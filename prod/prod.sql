CREATE DATABASE industria_textil;
USE industria_textil;

CREATE TABLE Fornecedor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    contato VARCHAR(255),
    cep VARCHAR(255) NOT NULL,
    CONSTRAINT FORNECEDOR_UN UNIQUE(NOME, CEP)
);

CREATE TABLE TipoFio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cor VARCHAR(60) NOT NULL,
    descricao VARCHAR(255) NOT NULL
);

CREATE TABLE TipoCorante (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cor VARCHAR(60) NOT NULL,
    descricao VARCHAR(255) NOT NULL
);

CREATE TABLE Fio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_barra CHAR(12) UNIQUE NOT NULL,
    tipo_fio_id INT,
    fornecedor_id INT,
    metragem DECIMAL(11, 2),
    em_estoque BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (tipo_fio_id) REFERENCES TipoFio(id),
    FOREIGN KEY (fornecedor_id) REFERENCES Fornecedor(id),
    CONSTRAINT METRAGEM_CK CHECK(METRAGEM > 0 AND METRAGEM <= 100000)

);

CREATE TABLE Corante (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_barra CHAR(12) UNIQUE NOT NULL,
    tipo_corante_id INT,
    fornecedor_id INT,
    litros DECIMAL(11, 2),
    em_estoque BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (tipo_corante_id) REFERENCES TipoCorante(id),
    FOREIGN KEY (fornecedor_id) REFERENCES Fornecedor(id),
    CONSTRAINT CORANTE_CK CHECK(LITROS > 0)
);

CREATE TABLE OrdemProducao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_barra CHAR(12) UNIQUE NOT NULL,
    metros_produzidos DECIMAL(11, 2),
    fio_id INT,
    corante_id INT,
    data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fim TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Em processamento',
    FOREIGN KEY (fio_id) REFERENCES Fio(id),
    FOREIGN KEY (corante_id) REFERENCES Corante(id),
    CONSTRAINT METROS_CK CHECK(METROS_PRODUZIDOS >= 0 AND METROS_PRODUZIDOS <= 100)
);

CREATE TABLE ProdutoFinal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_barra CHAR(12) UNIQUE NOT NULL,
    ordem_producao_id INT,
    tipo_corante_id INT,
    tipo_fio_id INT,
    CONSTRAINT PROD_FIN_UN UNIQUE(ordem_producao_id, tipo_corante_id, tipo_fio_id),
    FOREIGN KEY (ordem_producao_id) REFERENCES OrdemProducao(id),
    FOREIGN KEY (tipo_corante_id) REFERENCES TipoCorante(id),
    FOREIGN KEY (tipo_fio_id) REFERENCES TipoFio(id)
);

INSERT INTO Fornecedor (nome, contato, cep) VALUES 
('Fornecedor Têxtil Brasil', 'contato@texbr.com', '12345-678'),
('Fios & Corantes SA', 'contato@fiosec.com', '98765-432'),
('Tecelagem Modern', 'contato@modern.com', '45678-123'),
('Industria de Fios Ltda', 'contato@fiosltda.com', '87654-321');

INSERT INTO TipoFio (cor, descricao) VALUES 
('Branco', 'Fio de algodão branco para confecção'),
('Azul', 'Fio de poliéster azul para malharia'),
('Verde', 'Fio de lã verde para tecidos pesados'),
('Vermelho', 'Fio de nylon vermelho para roupas esportivas');

INSERT INTO TipoCorante (cor, descricao) VALUES 
('Branco', 'Corante branco para tingimento de tecidos leves'),
('Azul', 'Corante azul para tingimento de tecidos sintéticos'),
('Verde', 'Corante verde para tingimento de lã'),
('Vermelho', 'Corante vermelho para tingimento de roupas esportivas');

INSERT INTO Fio (codigo_barra, tipo_fio_id, fornecedor_id, metragem, em_estoque) VALUES 
('123456789012', 1, 1, 10000.50, TRUE),
('234567890123', 2, 2, 5000.25, TRUE),
('345678901234', 3, 3, 7500.00, FALSE),
('456789012345', 4, 4, 6000.75, TRUE);

INSERT INTO Corante (codigo_barra, tipo_corante_id, fornecedor_id, litros, em_estoque) VALUES 
('567890123456', 1, 1, 250.00, TRUE),
('678901234567', 2, 2, 300.50, TRUE),
('789012345678', 3, 3, 150.25, FALSE),
('890123456789', 4, 4, 400.00, TRUE);

INSERT INTO OrdemProducao (codigo_barra, metros_produzidos, fio_id, corante_id, data_fim) VALUES 
('901234567890', 50.75, 1, 1, '2024-09-06 12:00:00'),
('012345678901', 70.25, 2, 2, '2024-09-06 14:00:00'),
('123456789012', 40.50, 3, 3, '2024-09-07 10:00:00'),
('234567890123', 90.00, 4, 4, '2024-09-07 16:00:00');

INSERT INTO ProdutoFinal (codigo_barra, ordem_producao_id, tipo_corante_id, tipo_fio_id) VALUES 
('345678901234', 1, 1, 1),
('456789012345', 2, 2, 2),
('567890123456', 3, 3, 3),
('678901234567', 4, 4, 4);

