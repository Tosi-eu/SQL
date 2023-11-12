CREATE TABLE time (
    nome VARCHAR(35),
    estado CHAR(2) NOT NULL,
    tipo VARCHAR(12) NOT NULL CHECK (TIPO IN ('AMADOR', 'PROFISSIONAL')),
    saldo_gols INT DEFAULT 0,
    PRIMARY KEY(nome)
);  

CREATE TABLE joga (
    time1 VARCHAR(35) NOT NULL,
    time2 VARCHAR(35) NOT NULL,
    classico char(1) CHECK(classico IN('S', 'N')),
    PRIMARY KEY (time1, time2),
    CONSTRAINT time1_joga FOREIGN KEY (time1) REFERENCES time(nome) ON DELETE CASCADE,
    CONSTRAINT time2_joga FOREIGN KEY (time2) REFERENCES time(nome) ON DELETE CASCADE
);

CREATE TABLE partida (
    time1 VARCHAR(35),
    time2 VARCHAR(35),
    data_partida DATE NOT NULL,
    placar VARCHAR(5) DEFAULT '0x0' CHECK (PLACAR ~ '^[0-9]+x[0-9]+$'),
    local_partida VARCHAR(30) NOT NULL,
    PRIMARY KEY (time1, time2, data_partida),
    CONSTRAINT chave_partida FOREIGN KEY(time1, time2) REFERENCES joga(time1, time2) ON DELETE CASCADE
);

CREATE TABLE jogador (
    cpf VARCHAR(14),
    rg VARCHAR(12),
    nome VARCHAR(30) NOT NULL,
    data_nasc DATE NOT NULL,
    naturalidade VARCHAR(3) NOT NULL,
    time VARCHAR(35) NOT NULL,
    PRIMARY KEY(cpf),
	UNIQUE(rg, nome),
	CONSTRAINT time_atual FOREIGN KEY(time) REFERENCES time(nome) ON DELETE RESTRICT 
	);

CREATE TABLE posicao_jogador (
    jogador VARCHAR(35),
    posicao VARCHAR(30),
    PRIMARY KEY (jogador, posicao),
    CONSTRAINT onde_joga FOREIGN KEY(jogador) REFERENCES jogador(cpf) ON DELETE CASCADE 
);

CREATE TABLE diretor (
    time VARCHAR(35),
    nome VARCHAR(30),
    PRIMARY KEY (time, nome),
    CONSTRAINT onde_dirige FOREIGN KEY (time) REFERENCES TIME (nome) ON DELETE CASCADE
);

CREATE TABLE uniforme (
    time VARCHAR(30),
    tipo VARCHAR(30) CHECK (TIPO IN ('TITULAR', 'RESERVA')),
    cor_principal VARCHAR(30) NOT NULL,
    PRIMARY KEY (time, tipo),
    CONSTRAINT uniforme_time FOREIGN KEY (time) REFERENCES time(nome) ON DELETE CASCADE
);

