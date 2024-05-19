CREATE TABLE partido(
	codPartido SERIAL PRIMARY KEY,
	programa VARCHAR(255) NOT NULL,
	nome VARCHAR(60) NOT NULL,
	
	CONSTRAINT partido_un UNIQUE(programa, nome)
	);
	
CREATE TABLE cargo(
	codCargo SERIAL PRIMARY KEY,
	localidade VARCHAR(60) NOT NULL,
	qtdEleitos INTEGER NOT NULL
);

CREATE TABLE pleito(
	codPleito SERIAL PRIMARY KEY,
	qtdVotos INTEGER NOT NULL
);

CREATE TABLE programaPartido(
	codPrograma SERIAL PRIMARY KEY,
	descricao VARCHAR(255) UNIQUE NOT NULL,
	
	CONSTRAINT programa_fk FOREIGN KEY(codPrograma) REFERENCES partido(codPartido) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE processoJuridico(
	codProcesso SERIAL PRIMARY KEY,
	codIndividuo INTEGER NOT NULL,
	dataTermino DATE NOT NULL,
	procedente VARCHAR(60) NOT NULL
);

CREATE TABLE candidato(
	codCandidato SERIAL PRIMARY KEY,
	partido INTEGER UNIQUE NOT NULL,
	estadoFicha VARCHAR(5) NOT NULL,
	processos INTEGER,
	
	CONSTRAINT ck_partido CHECK(UPPER(estadoFicha) IN ('LIMPA', 'SUJA')),
	CONSTRAINT candidato_fk FOREIGN KEY(partido) REFERENCES partido(codPartido) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT candidato_processos_fk FOREIGN KEY(processos) REFERENCES processoJuridico(codProcesso) ON DELETE RESTRICT ON UPDATE CASCADE
	);

CREATE TABLE equipesApoio(
	codEquipe SERIAL PRIMARY KEY,
	nome VARCHAR(60) UNIQUE NOT NULL
);
	
CREATE TABLE participantesEquipesApoio(
	codParticipante SERIAL PRIMARY KEY,
	estadoFicha VARCHAR(5),
	equipe INTEGER UNIQUE NOT NULL,
	processo INTEGER,
	
	CONSTRAINT estado_ck CHECK(UPPER(estadoFicha) IN('LIMPA', 'SUJA')),
	CONSTRAINT equipe_fk FOREIGN KEY(equipe) REFERENCES equipesApoio(codEquipe) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT participantes_processos_fk FOREIGN KEY(processo) REFERENCES processoJuridico(codProcesso) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE doadorCampanha(
	codDoador INTEGER PRIMARY KEY,
	estadoFicha VARCHAR(5) NOT NULL,
	tipoDoador VARCHAR(30) NOT NULL,
	processo INTEGER,
	
	CONSTRAINT estado_ck CHECK(UPPER(estadoFicha) IN('LIMPA', 'SUJA')),
	CONSTRAINT doador_ck CHECK(UPPER(tipoDoador) IN('FÍSICO', 'JURÍDICO')),
	CONSTRAINT participantes_processos_fk FOREIGN KEY(processo) REFERENCES processoJuridico(codProcesso) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE doadorFisico(
	CPF INTEGER PRIMARY KEY,
	tipo VARCHAR(30),
	
	CONSTRAINT doador_f_fk FOREIGN KEY(CPF) REFERENCES doadorCampanha(codDoador) ON DELETE RESTRICT ON UPDATE CASCADE
	);

CREATE TABLE doadorJuridico(
	CNPJ INTEGER PRIMARY KEY,
	tipo VARCHAR(30),
	
	CONSTRAINT doador_f_fk FOREIGN KEY(CNPJ) REFERENCES doadorCampanha(codDoador) ON DELETE RESTRICT ON UPDATE CASCADE
	);
	
CREATE TABLE candidatura(
	codCandidatura SERIAL PRIMARY KEY,
	codCandidato INTEGER NOT NULL,
	codCargo INTEGER NOT NULL,
	codCandidaturaVice INTEGER NOT NULL,
	pleito INTEGER NOT NULL,
	codDoador INTEGER,
	
	CONSTRAINT candidatura_fk UNIQUE(codCandidato, codCargo, codCandidaturaVice, pleito),
	
	CONSTRAINT candidatura2_fk FOREIGN KEY(codCandidato) REFERENCES candidato(codCandidato) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT cargo_fk FOREIGN KEY(codCargo) REFERENCES cargo(codCargo) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT cand_vice_fk FOREIGN KEY(codCandidaturaVice) REFERENCES candidato(codCandidato) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT pleito_fk FOREIGN KEY(pleito) REFERENCES pleito(codPleito) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT doador_fk FOREIGN KEY(codDoador) REFERENCES doadorCampanha(codDoador) ON DELETE SET NULL ON UPDATE CASCADE
);
	
CREATE TABLE doa(
	codCandidatura INTEGER,
	codDoador INTEGER,
	valor NUMERIC(8, 2),
	
	CONSTRAINT doa_pk PRIMARY KEY(codCandidatura),
	CONSTRAINT candidatura_fk FOREIGN KEY(codCandidatura) REFERENCES candidatura(codCandidatura) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT doador_fk FOREIGN KEY(codDoador) REFERENCES doadorCampanha(codDoador) ON DELETE RESTRICT ON UPDATE CASCADE
	);

CREATE TABLE apoiam(
	codCandidatura INTEGER PRIMARY KEY,
	codEquipe INTEGER UNIQUE NOT NULL,
	
	CONSTRAINT candidatura_fk FOREIGN KEY(codCandidatura) REFERENCES candidatura(codCandidatura) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT equipe_fk FOREIGN KEY(codEquipe) REFERENCES equipesApoio(codEquipe) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE participam(
	codParticipante INTEGER,
	codEquipe INTEGER,
	ano DATE,
	
	CONSTRAINT participam_pk PRIMARY KEY(codParticipante, codEquipe, ano),
	CONSTRAINT participante_fk FOREIGN KEY(codParticipante) REFERENCES participantesEquipesApoio(codParticipante) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT equipe_fk FOREIGN KEY(codEquipe) REFERENCES equipesApoio(codEquipe) ON DELETE CASCADE ON UPDATE CASCADE
);
