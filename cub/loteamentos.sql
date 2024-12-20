CREATE TABLE CLIENTES(
	CLIENTE_ID INT PRIMARY KEY,
	NOME VARCHAR(60) NOT NULL,
	CPF_CNPJ VARCHAR(14) NOT NULL,
	EMAIL VARCHAR(60) NOT NULL,
	STATUS  VARCHAR(7) DEFAULT 'Inativo',
	
	CONSTRAINT NOME_UN UNIQUE(NOME),
	CONSTRAINT CAD_UN UNIQUE(CPF_CNPJ),
	CONSTRAINT EMAIL_UN UNIQUE(EMAIL),
	
	CONSTRAINT STATUS_CK CHECK(UPPER(STATUS) IN('ATIVO', 'INATIVO'))
	
);

CREATE TABLE UNIDADES(
	UNIDADE_ID INT PRIMARY KEY,
	LOTEAMENTO VARCHAR(60) NOT NULL,
	QUADRA VARCHAR(60) NOT NULL,
	LOTE VARCHAR(9) NOT NULL,
	VALOR DECIMAL(11, 2) NOT NULL,
	
	CONSTRAINT LOTEAMENTO_UN UNIQUE(LOTEAMENTO, QUADRA, LOTE),
	CONSTRAINT VALOR_CK CHECK(VALOR > 0.0)
);
	
CREATE TABLE CONTRATOS(
	
	CONTRATO_ID INT PRIMARY KEY,
	CLIENTE_ID INT,
	UNIDADE_ID INT,
	DATA_CONTRATO DATE NOT NULL,
	VALOR_TOTAL DECIMAL(11, 2) NOT NULL,
	
	CONSTRAINT CLIENTE_FK FOREIGN KEY(CLIENTE_ID) REFERENCES CLIENTES(CLIENTE_ID) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT UNIDADE_FK FOREIGN KEY(UNIDADE_ID) REFERENCES UNIDADES(UNIDADE_ID) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT DATA_CK CHECK(DATA_CONTRATO <= CURRENT_DATE),
	CONSTRAINT VALOR_CK CHECK(VALOR_TOTAL > 0.0)
);	

CREATE TABLE PARCELAS(
	PARCELA_ID INT PRIMARY KEY,
	CONTRATO_ID INT,
	DATA_VENCIMENTO DATE NOT NULL,
	VALOR_PARCELA DECIMAL(11, 2),
	STATUS VARCHAR(8) DEFAULT 'Pendente',
	
	CONSTRAINT CONTRATO_FK FOREIGN KEY(CONTRATO_ID) REFERENCES CONTRATOS(CONTRATO_ID) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT PARCELA_CK CHECK(VALOR_PARCELA > 0.0),
	CONSTRAINT PARC_STATUS_CK CHECK(UPPER(STATUS) IN ('PENDENTE', 'PAGA', 'VENCIDA'))
);

CREATE TABLE PAGAMENTOS(
	
	PAGAMENTO_ID INT PRIMARY KEY,
	PARCELA_ID INT,
	DATA_PAGAMENTO DATE NOT NULL,
	VALOR_PAGO DECIMAL(11, 2) NOT NULL,
	
	CONSTRAINT PARCELA_FK FOREIGN KEY(PARCELA_ID) REFERENCES PARCELAS(PARCELA_ID) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT DATA_CK CHECK(DATA_PAGAMENTO <= CURRENT_DATE),
	CONSTRAINT VALOR_CK CHECK(VALOR_PAGO > 0.0)
);

CREATE OR REPLACE FUNCTION atualizar_status_parcela()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.VALOR_PAGO >= (SELECT VALOR_PARCELA FROM PARCELAS WHERE PARCELA_ID = NEW.PARCELA_ID) THEN
        UPDATE PARCELAS
        SET STATUS = 'Paga'
        WHERE PARCELA_ID = NEW.PARCELA_ID;
	END IF;
    
    IF (SELECT DATA_VENCIMENTO FROM PARCELAS WHERE PARCELA_ID = NEW.PARCELA_ID) < CURRENT_DATE
        AND (SELECT STATUS FROM PARCELAS WHERE PARCELA_ID = NEW.PARCELA_ID) <> 'Paga' THEN
        UPDATE PARCELAS
        SET STATUS = 'Vencida'
        WHERE PARCELA_ID = NEW.PARCELA_ID;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_atualizar_status_parcela
AFTER INSERT ON PAGAMENTOS
FOR EACH ROW
EXECUTE FUNCTION atualizar_status_parcela();

CREATE OR REPLACE FUNCTION verificar_pagamento_redundante()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT STATUS FROM PARCELAS WHERE PARCELA_ID = NEW.PARCELA_ID) = 'Paga' THEN
        RAISE EXCEPTION 'A parcela já foi paga e não pode ser paga novamente';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_verificar_pagamento_redundante
BEFORE INSERT ON PAGAMENTOS
FOR EACH ROW
EXECUTE FUNCTION verificar_pagamento_redundante();

CREATE OR REPLACE FUNCTION atualizar_status_cliente()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM CONTRATOS WHERE CLIENTE_ID = NEW.CLIENTE_ID)
	AND (SELECT STATUS FROM CLIENTES WHERE CLIENTE_ID = NEW.CLIENTE_ID) = 'Ativo'
	THEN
        
        UPDATE CLIENTES SET STATUS = 'Inativo'
			WHERE CLIENTE_ID = NEW.CLIENTE_ID;
	ELSE
		UPDATE CLIENTES
		SET STATUS = 'Ativo'
		WHERE CLIENTE_ID = OLD.CLIENTE_ID;
    END IF;
    
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_atualizar_status_cliente
AFTER DELETE ON CONTRATOS
FOR EACH ROW
EXECUTE FUNCTION atualizar_status_cliente();

CREATE OR REPLACE FUNCTION verificar_status_invalido()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.STATUS = 'Ativo' THEN
        RAISE EXCEPTION 'Novos usuários ainda não possuem contratos ativos';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_verificar_status_invalido
BEFORE INSERT ON CLIENTES
FOR EACH ROW
EXECUTE FUNCTION verificar_status_invalido();

CREATE OR REPLACE FUNCTION verificar_stauts_parcela_insercao()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.DATA_VENCIMENTO < CURRENT_DATE AND NEW.STATUS <> 'Vencida' THEN
		RAISE NOTICE 'Atualizando status da parcela como vencida';
		UPDATE PARCELAS SET STATUS = 'Vencida' WHERE PARCELA_ID = NEW.PARCELA_ID;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_verificar_stauts_parcela_insercao
AFTER INSERT ON PARCELAS
FOR EACH ROW
EXECUTE FUNCTION verificar_stauts_parcela_insercao();

CREATE OR REPLACE FUNCTION validar_valor_pagamento()
RETURNS TRIGGER AS $$
DECLARE
    v_parcela DECIMAL(11, 2);
BEGIN
    SELECT VALOR_PARCELA INTO v_parcela FROM PARCELAS WHERE PARCELA_ID = NEW.PARCELA_ID;

    IF NEW.VALOR_PAGO > v_parcela THEN
        RAISE EXCEPTION 'O valor pago não pode ser maior que o valor da parcela';
    ELSIF NEW.VALOR_PAGO < v_parcela THEN
        RAISE EXCEPTION 'O valor pago não pode ser menor que o valor da parcela';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validar_valor_pagamento
BEFORE INSERT ON PAGAMENTOS
FOR EACH ROW
EXECUTE FUNCTION validar_valor_pagamento();

