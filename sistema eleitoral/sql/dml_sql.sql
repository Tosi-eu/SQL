-- Gabriel Garcia Ferreira - 13677160
-- Aruan Bretas de Oliveira Filho - 12609731
-- Guilherme Henrique Galdini Tosi 11781587
-- Antonio Rodrigues Rigolino - 11795791

-- Inserções na tabela Pleito
INSERT INTO Pleito (Cod_Pleito, Qtd_Votos) VALUES
(1, 1000),
(2, 1500),
(3, 2000),
(4, 1800),
(5, 2200),
(6, 2500);

-- Inserções na tabela EquipeApoio
INSERT INTO EquipeApoio (Cod_Equipe, Nome) VALUES
(1, 'Equipe 1'),
(2, 'Equipe 2'),
(3, 'Equipe 3'),
(4, 'Equipe 4'),
(5, 'Equipe 5'),
(6, 'Equipe 6');

-- Inserções na tabela Individuo
INSERT INTO Individuo (CPF, Nome, Ficha_Limpa, Cod_Equipe) VALUES
('111.111.111-11', 'Fulano', TRUE, 1),
('222.222.222-22', 'Ciclano', TRUE, 2),
('333.333.333-33', 'Beltrano', TRUE, 3),
('444.444.444-44', 'João', TRUE, 4),
('555.555.555-55', 'Maria', TRUE, 5),
('666.666.666-66', 'José', TRUE, 6);

-- Inserções na tabela Cargo
INSERT INTO Cargo (Cod_Cargo, Descricao, Localidade, Qtd_Eleitos, Pais, Estado, Cidade) VALUES
(1, 'Prefeito', 'MUNICIPAL', 1, 'BRASIL', 'São Paulo', 'São Paulo'),
(2, 'Governador', 'ESTADUAL', 1, 'BRASIL', 'Rio de Janeiro', NULL),
(3, 'Senador', 'FEDERAL', 2, 'BRASIL', NULL, NULL),
(4, 'Deputado Estadual', 'ESTADUAL', 5, 'BRASIL', 'Minas Gerais', NULL),
(5, 'Deputado Federal', 'FEDERAL', 10, 'BRASIL', NULL, NULL),
(6, 'Vereador', 'MUNICIPAL', 3, 'BRASIL', 'Porto Alegre', 'Rio Grande do Sul');

-- Inserções na tabela ProgramaPartido
INSERT INTO ProgramaPartido (Cod_Programa, Descricao) VALUES
(1, 'Programa A'),
(2, 'Programa B'),
(3, 'Programa C'),
(4, 'Programa D'),
(5, 'Programa E'),
(6, 'Programa F');

-- Inserções na tabela Partido
INSERT INTO Partido (Cod_Partido, Nome, Cod_Programa) VALUES
(1, 'Partido 1', 1),
(2, 'Partido 2', 2),
(3, 'Partido 3', 3),
(4, 'Partido 4', 4),
(5, 'Partido 5', 5),
(6, 'Partido 6', 6);

-- Inserções na tabela Candidatura
INSERT INTO Candidatura (Cod_Candidatura, Cod_Candidato, Cod_Cargo, Cod_Partido, Ano, Cod_Pleito, Cod_Candidatura_Vice, Eleito, Total_Doacoes) VALUES
(1, '111.111.111-11', 1, 1, 2024, 1, NULL, FALSE, 0),
(2, '222.222.222-22', 2, 2, 2024, 2, NULL, FALSE, 0),
(3, '333.333.333-33', 3, 3, 2024, 3, NULL, FALSE, 0),
(4, '444.444.444-44', 4, 4, 2024, 4, NULL, FALSE, 0),
(5, '555.555.555-55', 5, 5, 2024, 5, NULL, FALSE, 0),
(6, '666.666.666-66', 6, 6, 2024, 6, NULL, FALSE, 0);

-- Inserções na tabela ProcessoJudicial
INSERT INTO ProcessoJudicial (Cod_Processo, Cod_Individuo, Data_Inicio, Julgado, Data_Termino, Procedente) VALUES
(1, '444.444.444-44', '2023-01-01', TRUE, '2023-02-01', TRUE),
(2, '666.666.666-66', '2023-03-01', TRUE, '2023-04-01', FALSE),
(3, '222.222.222-22', '2023-05-01', FALSE, NULL, NULL),
(4, '555.555.555-55', '2023-06-01', TRUE, '2023-07-01', TRUE),
(5, '111.111.111-11', '2023-08-01', FALSE, NULL, NULL),
(6, '333.333.333-33', '2023-09-01', TRUE, '2023-10-01', FALSE);

-- Inserções na tabela Empresa
INSERT INTO Empresa (CNPJ, Nome) VALUES
('01.234.567/0001-89', 'Empresa A'),
('12.345.678/0001-90', 'Empresa B'),
('23.456.789/0001-91', 'Empresa C'),
('34.567.890/0001-92', 'Empresa D'),
('45.678.901/0001-93', 'Empresa E'),
('56.789.012/0001-94', 'Empresa F');

-- Inserções na tabela DoacaoPF
INSERT INTO DoacaoPF (Cod_Nota, Cod_Individuo, Valor, data_doacao) VALUES
(1, '111.111.111-11', 500.00, '2024-01-01'),
(2, '222.222.222-22', 1000.00, '2024-02-01'),
(3, '333.333.333-33', 1500.00, '2024-02-15'),
(4, '444.444.444-44', 2000.00, '2024-03-01'),
(5, '555.555.555-55', 2500.00, '2024-03-15'),
(6, '666.666.666-66', 3000.00, '2024-04-01'),
(7, '222.222.222-22', 4000.00, '2024-05-01');

INSERT INTO DoadorPJ (Cod_Candidatura, Cod_Empresa, Valor, data_doacao) VALUES
(1, '01.234.567/0001-89', 5000.00, '2024-01-01'),
(2, '12.345.678/0001-90', 6000.00, '2024-02-01'),
(3, '23.456.789/0001-91', 7000.00, '2024-03-01'),
(4, '34.567.890/0001-92', 8000.00, '2024-04-01'),
(5, '45.678.901/0001-93', 9000.00, '2024-05-01'),
(6, '56.789.012/0001-94', 10000.00, '2024-06-01');
