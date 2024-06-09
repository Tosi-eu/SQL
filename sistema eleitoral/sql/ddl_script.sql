-- Gabriel Garcia Ferreira - 13677160
-- Aruan Bretas de Oliveira Filho - 12609731
-- Guilherme Henrique Galdini Tosi 11781587
-- Antonio Rodrigues Rigolino - 11795791
CREATE TABLE Pleito (
    Cod_Pleito INTEGER PRIMARY KEY,
    Qtd_Votos INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE EquipeApoio (
    Cod_Equipe INTEGER PRIMARY KEY,
	Nome VARCHAR(50)
);

CREATE TABLE Individuo(
	CPF VARCHAR(14) PRIMARY KEY,
	Nome VARCHAR(50) NOT NULL,
	Ficha_Limpa BOOLEAN NOT NULL DEFAULT TRUE,
	Cod_Equipe INTEGER DEFAULT NULL,
	FOREIGN KEY (Cod_Equipe) REFERENCES EquipeApoio(Cod_Equipe) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Cargo (
    Cod_Cargo INTEGER PRIMARY KEY,
	Descricao VARCHAR(50),
    Localidade VARCHAR(50),
    Qtd_Eleitos INTEGER NOT NULL,
    Pais VARCHAR(50) NOT NULL DEFAULT 'BRASIL',
    Estado VARCHAR(50),
    Cidade VARCHAR(50),

    CHECK (Localidade IN ('MUNICIPAL','ESTADUAL','FEDERAL'))

);

CREATE TABLE ProgramaPartido(
	Cod_Programa INTEGER PRIMARY KEY,
	Descricao VARCHAR(250) UNIQUE NOT NULL
);

CREATE TABLE Partido(
	Cod_Partido INTEGER PRIMARY KEY,
	Nome VARCHAR(50) NOT NULL UNIQUE,
	Cod_Programa INTEGER NOT NULL,
	
	FOREIGN KEY (Cod_Programa) REFERENCES ProgramaPartido(Cod_Programa) ON DELETE CASCADE ON UPDATE CASCADE
	
);

CREATE TABLE Candidatura (
    Cod_Candidatura INTEGER PRIMARY KEY,
    Cod_Candidato VARCHAR(14) NOT NULL,
    Cod_Cargo INTEGER NOT NULL,
	Cod_Partido INTEGER NOT NULL, 
    Ano INTEGER NOT NULL,
    Cod_Pleito INTEGER NOT NULL,
    Cod_Candidatura_Vice INTEGER,
    Eleito BOOLEAN DEFAULT FALSE,
    Total_Doacoes INTEGER DEFAULT 0,
	
    FOREIGN KEY (Cod_Candidato) REFERENCES Individuo(CPF) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Cod_Cargo) REFERENCES Cargo(Cod_Cargo) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (Cod_Partido) REFERENCES Partido(Cod_Partido) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Cod_Pleito) REFERENCES Pleito(Cod_Pleito) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Cod_Candidatura_Vice) REFERENCES Candidatura(Cod_Candidatura) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE ProcessoJudicial (
    Cod_Processo INTEGER PRIMARY KEY,
    Cod_Individuo VARCHAR(14) NOT NULL,
	Data_Inicio DATE NOT NULL,
	Julgado BOOLEAN NOT NULL,
    Data_Termino DATE,
    Procedente BOOLEAN,
	
    FOREIGN KEY (Cod_Individuo) REFERENCES Individuo(CPF) ON DELETE CASCADE ON UPDATE CASCADE,
	CHECK (Julgado = FALSE OR (Data_Termino IS NOT NULL AND Procedente IS NOT NULL))
);

CREATE TABLE Empresa (
    CNPJ VARCHAR(18) PRIMARY KEY,
    Nome VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE DoacaoPF(
	Cod_Nota INTEGER PRIMARY KEY,
	Cod_Individuo VARCHAR(14) NOT NULL,
	Valor NUMERIC(11, 2),
	data_doacao DATE,
	
	FOREIGN KEY (Cod_Individuo) REFERENCES Individuo(CPF) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE DoadorPJ(
	Cod_Candidatura INTEGER,
	Cod_Empresa VARCHAR(18),
	Valor NUMERIC(11,2),
	data_doacao DATE,
	
	CONSTRAINT pk_doaPJ PRIMARY KEY (Cod_Candidatura, Cod_Empresa),
	FOREIGN KEY (Cod_Empresa) REFERENCES Empresa(CNPJ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (Cod_Candidatura) REFERENCES Candidatura(Cod_Candidatura) ON DELETE CASCADE ON UPDATE CASCADE
);

--atualiza a ficha limpa caso individuo tenha problemas com  justiça
CREATE OR REPLACE FUNCTION atualizar_ficha_limpa() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.Julgado = TRUE AND NEW.Procedente = TRUE THEN
        UPDATE Individuo
        SET Ficha_Limpa = FALSE
        WHERE CPF = NEW.Cod_Individuo;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_atualizar_ficha_limpa
AFTER UPDATE ON ProcessoJudicial
FOR EACH ROW
WHEN (NEW.Julgado IS TRUE AND NEW.Procedente IS TRUE)
EXECUTE FUNCTION atualizar_ficha_limpa();

--verifica se o candidato é ficha limpa antes de inserir
CREATE OR REPLACE FUNCTION verificar_ficha_limpa() RETURNS TRIGGER AS $$
BEGIN
    IF NOT (SELECT Ficha_Limpa FROM Individuo WHERE CPF = NEW.Cod_Candidato) THEN
        RAISE EXCEPTION 'O candidato não tem a ficha limpa';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verificar_ficha_limpa
BEFORE INSERT ON Candidatura
FOR EACH ROW
EXECUTE FUNCTION verificar_ficha_limpa();

CREATE OR REPLACE FUNCTION check_valid_candidatura() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.Cod_Candidatura_Vice IS NOT NULL AND
       NOT EXISTS (SELECT 1 FROM Candidatura WHERE Cod_Candidatura = NEW.Cod_Candidatura_Vice) THEN
        RAISE EXCEPTION 'Invalid Vice Candidature';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_valid_candidatura
BEFORE INSERT OR UPDATE ON Candidatura
FOR EACH ROW EXECUTE FUNCTION check_valid_candidatura();

CREATE OR REPLACE FUNCTION atualizar_total_doacoes_pf() RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM DoacaoPF WHERE Cod_Nota = NEW.Cod_Nota) THEN
        -- Atualiza apenas a tabela Candidatura se a nota já existir
        UPDATE Candidatura
        SET Total_Doacoes = Total_Doacoes + NEW.Valor
        WHERE Cod_Candidatura = (SELECT Cod_Candidatura FROM Candidatura WHERE Cod_Candidato = NEW.Cod_Individuo);
		RETURN NULL;
    ELSE
        UPDATE Candidatura
        SET Total_Doacoes = Total_Doacoes + NEW.Valor
        WHERE Cod_Candidatura = (SELECT Cod_Candidatura FROM Candidatura WHERE Cod_Candidato = NEW.Cod_Individuo);
		RETURN NEW;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_atualizar_total_doacoes_pf
BEFORE INSERT ON DoacaoPF
FOR EACH ROW
EXECUTE FUNCTION atualizar_total_doacoes_pf();

--atribui o que foi doado ao valor total da campanha por empresas
CREATE OR REPLACE FUNCTION atualizar_total_doacoes_pj() RETURNS TRIGGER AS $$
BEGIN
    UPDATE Candidatura
    SET Total_Doacoes = Total_Doacoes + NEW.Valor
    WHERE Cod_Candidatura = NEW.Cod_Candidatura;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_atualizar_total_doacoes_pj
AFTER INSERT ON DoadorPJ
FOR EACH ROW
EXECUTE FUNCTION atualizar_total_doacoes_pj();

CREATE OR REPLACE FUNCTION valida_localidade()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.Localidade = 'ESTADUAL' AND NEW.Estado IS NULL THEN
        RAISE EXCEPTION 'Estado não pode ser NULL para localidade ESTADUAL';
    ELSIF NEW.Localidade = 'MUNICIPAL' AND (NEW.Estado IS NULL OR NEW.Cidade IS NULL) THEN
        RAISE EXCEPTION 'Estado e Cidade não podem ser NULL para localidade MUNICIPAL';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER verifica_localidade
BEFORE INSERT OR UPDATE ON Cargo
FOR EACH ROW
EXECUTE FUNCTION valida_localidade();

CREATE OR REPLACE FUNCTION check_cargo_limits() 
RETURNS TRIGGER AS $$
DECLARE
    max_allowed INTEGER;
    current_count INTEGER;
BEGIN
    CASE NEW.Cod_Cargo
        WHEN '1' THEN
            max_allowed := 1;
        WHEN '2' THEN
            max_allowed := 81;
        WHEN '3' THEN
            max_allowed := 513;
        WHEN '4' THEN
            max_allowed := 27;
        WHEN '5' THEN
            max_allowed := 1059;
        WHEN '6' THEN
            max_allowed := 5570;
        WHEN '7' THEN
            max_allowed := 57931;
        ELSE
            RAISE EXCEPTION 'Cargo não reconhecido: %', NEW.Cod_Cargo;
    END CASE;

    SELECT COUNT(*) INTO current_count 
    FROM Candidatura
    WHERE Cod_Cargo = NEW.Cod_Cargo AND Eleito = TRUE AND Ano = NEW.Ano;

    IF NEW.Eleito = TRUE AND current_count >= max_allowed THEN
        RAISE EXCEPTION 'Limite de eleitos para o cargo % excedido. Máximo permitido: %', NEW.Cod_Cargo, max_allowed;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_cargo_limits_trigger
BEFORE INSERT OR UPDATE ON Candidatura
FOR EACH ROW
EXECUTE FUNCTION check_cargo_limits();

CREATE OR REPLACE FUNCTION check_unique_candidacy_per_year()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM Candidatura
        WHERE Cod_Candidato = NEW.Cod_Candidato
        AND Ano = NEW.Ano
        AND Cod_Cargo <> NEW.Cod_Cargo
    ) THEN
        RAISE EXCEPTION 'O indivíduo % já possui uma candidatura registrada para outro cargo no ano %.', NEW.Cod_Candidato, NEW.Ano;
    ELSIF EXISTS (
        SELECT 1
        FROM Candidatura
        WHERE Cod_Candidato = NEW.Cod_Candidato
        AND Ano = NEW.Ano
        AND Cod_Cargo = NEW.Cod_Cargo
    ) THEN
        RAISE EXCEPTION 'O indivíduo % já possui uma candidatura registrada para esse cargo no ano %.', NEW.Cod_Candidato, NEW.Ano;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criação do trigger
CREATE TRIGGER check_unique_candidacy_per_year_trigger
BEFORE INSERT ON Candidatura
FOR EACH ROW
EXECUTE FUNCTION check_unique_candidacy_per_year();
