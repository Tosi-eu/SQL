CREATE TABLE ESTUDIO(
	codigo_estudio VARCHAR(30) PRIMARY KEY,
	nome_estudio VARCHAR(60) NOT NULL,
	rua VARCHAR(30) NOT NULL,
	bairro VARCHAR(30) NOT NULL,
	numero INT NOT NULL,
	cidade VARCHAR(50) NOT NULL,
	UF CHAR(2) NOT NULL
);

CREATE TABLE PRODUTORA(
	nome_produtora VARCHAR(60) NOT NULL,
	rua VARCHAR(30) NOT NULL,
	bairro VARCHAR(30) NOT NULL,
	numero INT NOT NULL,
	cidade VARCHAR(50) NOT NULL,
	UF CHAR(2) NOT NULL,
	codigo_produtora VARCHAR(30) PRIMARY KEY
);

CREATE TABLE FILME(
	titulo VARCHAR(60),
	ano INT,
	duracao DECIMAL NOT NULL,
	colorido CHAR(1) NOT NULL,
    estudio VARCHAR(60) NOT NULL,
    produtora VARCHAR(60) NOT NULL,
	PRIMARY KEY(titulo, ano),
	CONSTRAINT cores CHECK(UPPER(colorido)IN('S', 'N')),
	CONSTRAINT cod_estudio FOREIGN KEY(estudio) REFERENCES ESTUDIO(codigo_estudio) ON DELETE CASCADE,
	CONSTRAINT cod_produtora FOREIGN KEY(produtora) REFERENCES PRODUTORA(codigo_produtora) ON DELETE CASCADE
);

CREATE TABLE ATOR(
	nome VARCHAR(60) PRIMARY KEY,
	rua VARCHAR(30) NOT NULL,
	bairro VARCHAR(30) NOT NULL,
	numero INT NOT NULL,
	cidade VARCHAR(50) NOT NULL,
	UF CHAR(2) NOT NULL,
	sexo CHAR(1) NOT NULL,
	data_nascimento DATE,
	CONSTRAINT genero CHECK(UPPER(sexo)IN('M', 'F'))
);

CREATE TABLE ATUACAO(
	titulo_filme varchar(60) NOT NULL,
	ano_filme INT NOT NULL,
	nome_ator VARCHAR(60) NOT NULL,
	PRIMARY KEY(titulo_filme, ano_filme, nome_ator),
	CONSTRAINT nome_ator FOREIGN KEY(nome_ator) REFERENCES ATOR(nome) ON DELETE CASCADE,
	CONSTRAINT filme_titulo FOREIGN KEY(titulo_filme, ano_filme) REFERENCES FILME(titulo, ano) ON DELETE CASCADE
)
