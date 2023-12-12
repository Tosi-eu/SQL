CREATE TABLE Administrador (
    CF VARCHAR(11) PRIMARY KEY,
    Nome VARCHAR(255) NOT NULL,
    Planeta VARCHAR(50) NOT NULL,
    CG VARCHAR(20) NOT NULL,
    Nro INTEGER NOT NULL
);

CREATE TABLE Empregado (
    CF VARCHAR(11) PRIMARY KEY,
    Nome VARCHAR(255) NOT NULL,
    Planeta VARCHAR(50) NOT NULL,
    CG VARCHAR(20) NOT NULL,
    Nro INTEGER NOT NULL
);

CREATE TABLE Piloto (
    CP VARCHAR(11) PRIMARY KEY,
    CF VARCHAR(11) UNIQUE NOT NULL,
    Nome VARCHAR(255) NOT NULL,
    Planeta VARCHAR(50) NOT NULL,
    CG VARCHAR(20) NOT NULL,
    Nro INTEGER NOT NULL
);

CREATE TABLE Espaconave (
    Nro_Serie INTEGER PRIMARY KEY,
    Tipo VARCHAR(10) NOT NULL,
    Modelo VARCHAR(50) NOT NULL,
    CONSTRAINT CHECK_TIPO CHECK (UPPER(Tipo) IN ('CARGA', 'TRANSPORTE'))
);

CREATE TABLE Carga (
    Espaconave INTEGER PRIMARY KEY,
    Capacidade INTEGER NOT NULL,
    CONSTRAINT FK_Carga FOREIGN KEY (Espaconave) REFERENCES Espaconave(Nro_Serie) ON DELETE CASCADE
);

CREATE TABLE E_TRANSPORTE (
    Espaconave INTEGER PRIMARY KEY,
    Qnt_Assentos INTEGER NOT NULL,
    CONSTRAINT FK_Transporte FOREIGN KEY (Espaconave) REFERENCES Espaconave(Nro_Serie) ON DELETE CASCADE
);

CREATE TABLE Assento (
    Transporte INTEGER,
    Nro_Assento INTEGER,
    CONSTRAINT PK_Assento PRIMARY KEY (Transporte, Nro_Assento),
    CONSTRAINT FK_Assento FOREIGN KEY (Transporte) REFERENCES E_TRANSPORTE(Espaconave) ON DELETE CASCADE
);

CREATE TABLE Pilota (
    Piloto VARCHAR(11),
    Espaconave INTEGER,
    CONSTRAINT PK_Pilota PRIMARY KEY (Piloto, Espaconave),
    CONSTRAINT FK_Piloto FOREIGN KEY (Piloto) REFERENCES Piloto(CP) ON DELETE CASCADE,
    CONSTRAINT FK_Espaconave FOREIGN KEY (Espaconave) REFERENCES Espaconave(Nro_Serie) ON DELETE CASCADE
);

CREATE TABLE Servico (
    Codigo INTEGER PRIMARY KEY,
    Empregado VARCHAR(11) NOT NULL,
    Espaconave INTEGER NOT NULL,
    Data Date,
    CONSTRAINT FK_Empregado FOREIGN KEY (Empregado) REFERENCES Empregado(CF) ON DELETE CASCADE,
    CONSTRAINT FK_EspaconaveServico FOREIGN KEY (Espaconave) REFERENCES Espaconave(Nro_Serie) ON DELETE CASCADE
);

CREATE TABLE Problemas (
    Servico INTEGER,
    Tipo VARCHAR(25),
    Descricao VARCHAR(500) NOT NULL,
    Solucao VARCHAR(500),
    CONSTRAINT PK_Problemas PRIMARY KEY (Servico, Tipo),
    CONSTRAINT FK_Servico FOREIGN KEY (Servico) REFERENCES Servico(Codigo) ON DELETE CASCADE
);

CREATE TABLE C_Juridico (
    CCJ INTEGER PRIMARY KEY,
    CC INTEGER UNIQUE NOT NULL,
    Registro INTEGER NOT NULL,
    Nome VARCHAR(255) NOT NULL
);

CREATE TABLE C_Fisico (
    CCF INTEGER PRIMARY KEY,
    CC INTEGER UNIQUE NOT NULL,
    Registro INTEGER NOT NULL,
    Nome VARCHAR(255) NOT NULL,
    Nascimento DATE NOT NULL
);

CREATE TABLE Planeta (
    Nome VARCHAR(50) PRIMARY KEY,
    CG VARCHAR(20) NOT NULL
);

CREATE TABLE Viagem (
    Data DATE NOT NULL,
    Hora TIMESTAMP NOT NULL,
    Transporte INTEGER NOT NULL,
    Nro_Assento INTEGER NOT NULL,
    C_Fisico INTEGER NOT NULL,
    Nr_Assentos_Disponiveis INTEGER NOT NULL,
    Origem VARCHAR(50) NOT NULL,
    Hora_Saida TIMESTAMP NOT NULL,
    Destino VARCHAR(50) NOT NULL,
    Hora_Chegada TIMESTAMP NOT NULL,
    CONSTRAINT PK_Viagem PRIMARY KEY (Data, Hora, Transporte, Nro_Assento),
    CONSTRAINT FK_Assento1 FOREIGN KEY (Transporte, Nro_Assento) REFERENCES Assento(Transporte, Nro_Assento) ON DELETE CASCADE,
    CONSTRAINT FK_CFisico FOREIGN KEY (C_Fisico) REFERENCES C_Fisico(CCF) ON DELETE CASCADE,
    CONSTRAINT FK_Origem FOREIGN KEY (Origem) REFERENCES Planeta(Nome) ON DELETE CASCADE,
    CONSTRAINT FK_Destino FOREIGN KEY (Destino) REFERENCES Planeta(Nome) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION calcular_assentos_disponiveis()
RETURNS TRIGGER AS $$
DECLARE
    qnt_assentos_e_transporte INTEGER;
BEGIN
    -- Obter a quantidade total de assentos disponíveis na E_TRANSPORTE
    SELECT Qnt_Assentos
    INTO qnt_assentos_e_transporte
    FROM E_TRANSPORTE
    WHERE Espaconave = NEW.Transporte;

    -- Calcular o número de assentos ocupados para a mesma hora, data e transporte na tabela Viagem
    SELECT COUNT(*)
    INTO NEW.Nr_Assentos_Disponiveis
    FROM Viagem
    WHERE Data = NEW.Data
        AND Hora = NEW.Hora
        AND Transporte = NEW.Transporte;

    -- Subtrair os assentos ocupados da quantidade total de assentos disponíveis
    NEW.Nr_Assentos_Disponiveis := qnt_assentos_e_transporte - NEW.Nr_Assentos_Disponiveis;

    -- Garantir que o Nr_Assentos_Disponiveis não seja menor que zero
    IF NEW.Nr_Assentos_Disponiveis < 0 THEN
        NEW.Nr_Assentos_Disponiveis := 0;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calcular_assentos_disponiveis
BEFORE INSERT OR UPDATE ON Viagem
FOR EACH ROW
EXECUTE FUNCTION calcular_assentos_disponiveis();

CREATE TABLE Transporte (
    Cod_Transporte INTEGER PRIMARY KEY,
    Carga INTEGER NOT NULL,
    C_Juridico INTEGER NOT NULL,
    Data DATE,
    Carga_Origem VARCHAR(50) NOT NULL,
    Hora_Saida TIMESTAMP,
    CONSTRAINT FK_CargaTransporte FOREIGN KEY (CARGA) REFERENCES Carga(Espaconave) ON DELETE CASCADE,
    CONSTRAINT FK_CJuridico FOREIGN KEY (C_Juridico) REFERENCES C_Juridico(CCJ) ON DELETE CASCADE,
    CONSTRAINT FK_OrigemTransporte FOREIGN KEY (Carga_Origem) REFERENCES Planeta(Nome) ON DELETE CASCADE
);

CREATE TABLE Carga_Destino (
    Transporte INTEGER,
    Planeta VARCHAR(50),
    Hora_Chegada TIMESTAMP NOT NULL,
    CONSTRAINT PK_CargaDestino PRIMARY KEY (Transporte, Planeta),
    CONSTRAINT FK_CargaTransporteDestino FOREIGN KEY (Transporte) REFERENCES Transporte(Cod_Transporte) ON DELETE CASCADE,
    CONSTRAINT FK_PlanetaCargaDestino FOREIGN KEY (Planeta) REFERENCES Planeta(Nome) ON DELETE CASCADE
);

CREATE TABLE Parada (
    Data DATE NOT NULL,
    Hora TIMESTAMP NOT NULL,
    Transporte INTEGER NOT NULL,
    Nro_Assento INTEGER NOT NULL,
    Planeta VARCHAR(50),
    CONSTRAINT PK_Parada PRIMARY KEY (Data, Hora, Transporte, Nro_Assento, Planeta),
    CONSTRAINT FK_ParadaViagem FOREIGN KEY (Data, Hora, Transporte, Nro_Assento) REFERENCES Viagem(Data, Hora, Transporte, Nro_Assento) ON DELETE CASCADE,
    CONSTRAINT FK_ParadaPlaneta FOREIGN KEY (Planeta) REFERENCES Planeta(Nome) ON DELETE CASCADE
);