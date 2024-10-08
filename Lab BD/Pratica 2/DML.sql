INSERT INTO PATROCINADOR (ID, NOME, TIPO) 
VALUES (SEQ_PATROCINADOR_ID.NEXTVAL, 'Coca-Cola', 'Bebida');

INSERT INTO PATROCINADOR (ID, NOME, TIPO) 
VALUES (SEQ_PATROCINADOR_ID.NEXTVAL, 'Nike', 'Roupas Esportivas');

INSERT INTO PAIS (ID, NOME, CONTINENTE, POPULACAO) 
VALUES (SEQ_PAIS_ID.NEXTVAL, 'Brasil', 'SA', DEFAULT);

INSERT INTO PAIS (ID, NOME, CONTINENTE, POPULACAO) 
VALUES (SEQ_PAIS_ID.NEXTVAL, 'Japão', 'AS', 125000000);

INSERT INTO ATLETA (PASSAPORTE, NOME, DATA_NASC, IDADE) 
VALUES (SEQ_ATLETA_PASS.NEXTVAL, 'Maria Silva', TO_DATE('12-05-1995', 'DD-MM-YYYY'), 29);

INSERT INTO ATLETA (PASSAPORTE, NOME, DATA_NASC, IDADE) 
VALUES (SEQ_ATLETA_PASS.NEXTVAL, 'John Doe', TO_DATE('23-11-1988', 'DD-MM-YYYY'), 35);

INSERT INTO OLIMPIADA (ANO, SEDE, N_MODALIDADES, ORG_GERAL) 
VALUES (2020, 'Tóquio', 33, 2);

INSERT INTO OLIMPIADA (ANO, SEDE, N_MODALIDADES, ORG_GERAL) 
VALUES (2016, 'Rio de Janeiro', DEFAULT, 1);

INSERT INTO ORGANIZADOR_GERAL (ID, NOME, DATA_NASC) 
VALUES (1, 'Comitê Olímpico Brasileiro', TO_DATE('05-08-1980', 'DD-MM-YYYY'));

INSERT INTO ORGANIZADOR_GERAL (ID, NOME, DATA_NASC) 
VALUES (2, 'Comitê Olímpico Internacional', NULL);

INSERT INTO MODALIDADE (ID, NOME, N_COMPETIDORES, GENERO) 
VALUES (SEQ_MODALIDADE_ID.NEXTVAL, 'Futebol', DEFAULT, 'M');

INSERT INTO MODALIDADE (ID, NOME, N_COMPETIDORES, GENERO) 
VALUES (SEQ_MODALIDADE_ID.NEXTVAL, 'Natação', 8, 'F');

INSERT INTO MIDIA (ID, NOME) 
VALUES (SEQ_MIDIA_ID.NEXTVAL, 'TV Globo');

INSERT INTO MIDIA (ID, NOME) 
VALUES (SEQ_MIDIA_ID.NEXTVAL, 'ESPN');

INSERT INTO MIDIA (ID, NOME) 
VALUES (SEQ_MIDIA_ID.NEXTVAL, 'Netflix');

INSERT INTO MIDIA (ID, NOME) 
VALUES (SEQ_MIDIA_ID.NEXTVAL, 'Youtube');

INSERT INTO LOCAL (ID, NOME, CAPACIDADE, ZIPCODE) 
VALUES (SEQ_LOCAL_ID.NEXTVAL, 'Maracanã', DEFAULT, '20021-203');

INSERT INTO LOCAL (ID, NOME, CAPACIDADE, ZIPCODE) 
VALUES (SEQ_LOCAL_ID.NEXTVAL, 'Estádio Olímpico', 60000, '136-0075');

INSERT INTO DISPUTA (ID, HORA, DATA, MODALIDADE, PAIS1, PAIS2, VENCEDOR, LOCAL, OLIMPIADA) 
VALUES (SEQ_DISPUTA_ID.NEXTVAL, 15.5, TO_DATE('21-08-2016', 'DD-MM-YYYY'), 1, 4, 1, 1, 1, 2016);

INSERT INTO DISPUTA (ID, HORA, DATA, MODALIDADE, PAIS1, PAIS2, VENCEDOR, LOCAL, OLIMPIADA) 
VALUES (SEQ_DISPUTA_ID.NEXTVAL, 10.0, TO_DATE('23-07-2021', 'DD-MM-YYYY'), 1, 1, 4, 1, 7, 2016);

INSERT INTO EQUIPE (NOME, PAIS, ANO) 
VALUES ('Seleção Brasileira', 1, 2016);

INSERT INTO EQUIPE (NOME, PAIS, ANO) 
VALUES ('Seleção Japonesa', 4, 2016);

INSERT INTO TRANSMISSAO_TV(DISPUTA, MIDIA) 
VALUES(1, 1);

INSERT INTO TRANSMISSAO_TV(DISPUTA, MIDIA) 
VALUES(8, 6);

INSERT INTO PAIS_OLIMPIADA (PAIS, OLIMPIADA) 
VALUES (1, 2016);

INSERT INTO PAIS_OLIMPIADA (PAIS, OLIMPIADA) 
VALUES (4, 2016);

INSERT INTO ATLETA_EQUIPE (ATLETA, NOME_EQUIPE, EQUIPE_PAIS, EQUIPE_ANO) 
VALUES (1000, 'Seleção Brasileira', 1, 2016);

INSERT INTO ATLETA_EQUIPE (ATLETA, NOME_EQUIPE, EQUIPE_PAIS, EQUIPE_ANO) 
VALUES (1001, 'Seleção Japonesa', 4, 2016);

INSERT INTO EQUIPE_MODALIDADE (EQUIPE_NOME, EQUIPE_PAIS, EQUIPE_ANO, MODALIDADE) 
VALUES ('Seleção Brasileira', 1, 2016, 1);

INSERT INTO EQUIPE_MODALIDADE (EQUIPE_NOME, EQUIPE_PAIS, EQUIPE_ANO, MODALIDADE) 
VALUES ('Seleção Japonesa', 4, 2016, 1);

INSERT INTO PATROCINIO_ATLETA (PATROCINADOR, ATLETA, INICIO_CONTRATO, TEMPO_VIGENCIA, VALOR_CONTRATO) 
VALUES (1, 1000, TO_DATE('01-01-2016', 'DD-MM-YYYY'), 4, 1500000);

INSERT INTO PATROCINIO_ATLETA (PATROCINADOR, ATLETA, INICIO_CONTRATO, TEMPO_VIGENCIA, VALOR_CONTRATO) 
VALUES (3, 1001, TO_DATE('01-01-2020', 'DD-MM-YYYY'), 4, 2000000);

INSERT INTO TV (NOME, CANAL, ABERTA_FECHADA) 
VALUES ('TV Globo', 5, 'ABERTA');

INSERT INTO TV (NOME, CANAL, ABERTA_FECHADA) 
VALUES ('ESPN', 30, 'FECHADA');

INSERT INTO RADIO (NOME, FREQUENCIA) 
VALUES ('TV Globo', 98.1);

INSERT INTO RADIO (NOME, FREQUENCIA) 
VALUES ('ESPN', 89.3); 

INSERT INTO STREAMING (NOME, URL, ASSINATURA_GRATUITO) 
VALUES ('Netflix', 'www.netflix.com', 'ASSINATURA');

INSERT INTO STREAMING (NOME, URL, ASSINATURA_GRATUITO) 
VALUES ('Youtube', 'www.youtube.com', 'GRATUITO');

UPDATE PAIS
SET POPULACAO = 11781587
WHERE NOME = 'Brasil';
    
UPDATE PAIS
SET POPULACAO = 785188711
WHERE NOME = 'Japão';

DELETE FROM MIDIA
WHERE NOME = 'Netflix';

DELETE FROM MIDIA
WHERE NOME = 'Youtube';

ALTER TABLE EQUIPE ADD NUM_INTEGRANTES INT DEFAULT 9 CHECK (NUM_INTEGRANTES >= 1);

ALTER TABLE PAIS DISABLE CONSTRAINT PAIS_CK;
INSERT INTO PAIS (ID, NOME, CONTINENTE) VALUES (10, 'Antarctica', 'AN');
ALTER TABLE PAIS ENABLE CONSTRAINT PAIS_CK;

ALTER TABLE EQUIPE ADD NUM_INTEGRANTES INT DEFAULT 9 CHECK (NUM_INTEGRANTES >= 1);

ALTER TABLE PAIS DISABLE CONSTRAINT PAIS_CK;
INSERT INTO PAIS (ID, NOME, CONTINENTE) VALUES (10, 'Antarctica', 'AN');
ALTER TABLE PAIS ENABLE CONSTRAINT PAIS_CK;

ALTER TABLE EQUIPE ADD (OLIMPIADA_ANO INT);

ALTER TABLE EQUIPE
ADD CONSTRAINT EQUIPE_FK_OLIMPIADA
FOREIGN KEY (OLIMPIADA_ANO) REFERENCES OLIMPIADA(ANO) ON DELETE CASCADE;

ALTER TABLE PAIS DROP PRIMARY KEY;
ALTER TABLE PAIS DROP PRIMARY KEY CASCADE;

DESCRIBE PAIS;
DESCRIBE EQUIPE;

INSERT INTO EQUIPE (NOME, PAIS, ANO) VALUES ('EquipeTeste', 999, 2024);
