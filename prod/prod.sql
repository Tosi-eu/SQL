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
    codigo_barra VARCHAR(30) UNIQUE NOT NULL,
    tipo_fio_id INT,
    fornecedor_id INT,
    metragem DECIMAL(10, 0),
    em_estoque BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (tipo_fio_id) REFERENCES TipoFio(id) ON DELETE CASCADE,
    FOREIGN KEY (fornecedor_id) REFERENCES Fornecedor(id) ON DELETE SET NULL,
    CONSTRAINT METRAGEM_CK CHECK(METRAGEM > 0 AND METRAGEM <= 100000)

);

CREATE TABLE Corante (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_barra VARCHAR(30) UNIQUE NOT NULL,
    tipo_corante_id INT,
    fornecedor_id INT,
    litros DECIMAL(10, 0),
    em_estoque BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (tipo_corante_id) REFERENCES TipoCorante(id) ON DELETE CASCADE,
    FOREIGN KEY (fornecedor_id) REFERENCES Fornecedor(id) ON DELETE SET NULL,
    CONSTRAINT CORANTE_CK CHECK(LITROS > 0)
);

CREATE TABLE OrdemProducao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_barra VARCHAR(30) UNIQUE NOT NULL,
    metros_produzidos DECIMAL(10, 0),
    fio_id INT,
    corante_id INT,
    data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fim TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Em processamento',
    FOREIGN KEY (fio_id) REFERENCES Fio(id) ON DELETE CASCADE,
    FOREIGN KEY (corante_id) REFERENCES Corante(id) ON DELETE CASCADE,
    CONSTRAINT METROS_CK CHECK(METROS_PRODUZIDOS >= 0 AND METROS_PRODUZIDOS <= 100)
);

CREATE TABLE ProdutoFinal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_barra VARCHAR(30) UNIQUE NOT NULL,
    ordem_producao_id INT,
    tipo_corante_id INT,
    tipo_fio_id INT,
    CONSTRAINT PROD_FIN_UN UNIQUE(ordem_producao_id, tipo_corante_id, tipo_fio_id),
    FOREIGN KEY (ordem_producao_id) REFERENCES OrdemProducao(id) ON DELETE CASCADE,
    FOREIGN KEY (tipo_corante_id) REFERENCES TipoCorante(id) ON DELETE CASCADE,
    FOREIGN KEY (tipo_fio_id) REFERENCES TipoFio(id) ON DELETE CASCADE
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


