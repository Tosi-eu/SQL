--Inserindo times

--time de SP
INSERT INTO time VALUES('Corinthians', 'SP', 'PROFISSIONAL', 0);

--time do RJ
INSERT INTO time VALUES('Fluminense', 'RJ', 'PROFISSIONAL', 0);

-- Uniformes dos times
INSERT INTO uniforme VALUES('Corinthians', 'TITULAR', 'branco');
INSERT INTO uniforme VALUES('Corinthians', 'RESERVA', 'Preto');

INSERT INTO uniforme VALUES('Fluminense', 'TITULAR', 'Verde');
INSERT INTO uniforme VALUES('Fluminense', 'RESERVA', 'Branco');

-- Diretores dos times
INSERT INTO diretor VALUES('Fluminense', 'Diniz');
INSERT INTO diretor VALUES ('Corinthians', 'Duilio');

-- Jogadores 
INSERT INTO jogador VALUES('123456789-10', '123456789', 'Kano', TO_DATE('23/07/1988', 'dd/MM/YYYY'), 'BRA', 'Fluminense');
INSERT INTO jogador VALUES('123456789-11', '123456789', 'Yuri Alberto', TO_DATE('24/08/1993', 'dd/MM/YYYY'), 'BRA', 'Corinthians');

-- Posições dos jogadores

--Posição Kano
INSERT INTO posicao_jogador VALUES ('123456789-10', 'Atacante');

--Posição Yuri ALberto
INSERT INTO posicao_jogador VALUES ('123456789-11', 'Atacante');

-- Jogo entre os times
INSERT INTO joga VALUES ('Fluminense', 'Corinthians', 'N');

-- Partida firmada (como se fosse instância de joga)
INSERT INTO partida VALUES ('Fluminense', 'Corinthians', TO_DATE('11/11/2023', 'dd/MM/YYYY'), '1x2', 'Maracana');

-- Atualização de saldo de gols
UPDATE partida SET placar='2x3' WHERE time1='Fluminense' AND time2='Corinthians';

UPDATE time
    SET saldo_gols = 
        CASE 
            WHEN nome='Fluminense' THEN saldo_gols+2
            WHEN nome='Corinthians' THEN saldo_gols+3
            ELSE saldo_gols
        END;

UPDATE partida SET placar='2x0' WHERE time1='Fluminense' AND time2='Corinthians';
UPDATE time
    SET saldo_gols = 
        CASE 
            WHEN nome='Fluminense' THEN saldo_gols+2
            WHEN nome='Corinthians' THEN saldo_gols+0
            ELSE saldo_gols
        END;

-----restrições

--time não existe na tabela time
INSERT INTO jogador VALUES ('123456789-12', '123456789', 'Dedé', TO_DATE('11/12/1985', 'dd/MM/YYYY'), 'BRA', 'Coritiba');

--CPF repetido
INSERT INTO jogador VALUES ('123456789-10', '123456789', 'Dedé', TO_DATE('01/01/1985', 'dd/MM/YYYY'), 'BRA', 'Linense');

--nome e RG se repetem
INSERT INTO jogador VALUES ('123456789-14', '123456789', 'Dedé', TO_DATE('01/01/1985', 'dd/MM/YYYY'), 'BRA', 'Velo Clube');


--Exclusão do time de SP
DELETE FROM time WHERE estado='SP';

/* 
Não acontece, pois existem jogadores registrados, e a condição ON DELETE RESTRICT impele que o time não pode ser excluido se tiverem jogadores nele,
além do fato que jogador n fica sem time, diferente do que foi feito abaixo, que primeiro remove os jogadores e aí o time, que então possibilita dar certo, e pela condição
CASCADE, as tabelas DIRETOR, UNIFORME, JOGA, PARTIDA são  excluídas, pois possuem uma chave  estrangeira que referencia a chave primária da tabela Time.
*/

DELETE FROM jogador WHERE time='Corinthians';
DELETE FROM time WHERE estado='SP';

/* 
## Parte 3

a) Insira, na tabela Jogador, o atributo atômico endereço, que poderá assumir valor nulo. O que aconteceu nas tuplas que já existentes na tabela? 
R: Com a alteração, todos as instâncias de jogador existentes recebem NULL
*/

-- Inserindo o atributo endereço
ALTER TABLE jogador ADD endereco VARCHAR(100);

/* 
b) Faça o mesmo teste para um novo atributo qualquer com valor default. 
R: Como foi definido um valor "default" todos os jogadores receberão 0 na coluna salário em vez de NULL
*/

ALTER TABLE jogador ADD salario FLOAT DEFAULT 0;

/* 
c) escolha uma tabela e crie uma nova constraint do tipo check, de modo que os valores já existentes na 
tabela não atendam à nova restrição (faça as inserções necessárias para teste antes da criação da nova constraint). 

R: Ao efetuar a alteração da tabela jogador, é adicionada a constraint verifica_salario para todas as 
tuplas da tabela, porém como há tuplas que não atendem a condição, o que ocasiona ela ser invalidada, diferente do caso que se usa o NOT VALID, pois assim
a constraint n passa pelo processo de validação, e é inserida do msm jeito
*/

UPDATE jogador SET salario=5000 WHERE cpf='123456789-10';

UPDATE jogador SET salario=9999 WHERE cpf='123456789-11';

--nova constraint (invalidada)
ALTER TABLE jogador ADD CONSTRAINT verifica_salario CHECK (salario > 10000);

--nova constraint (não verificada, inserida)
ALTER TABLE jogador ADD CONSTRAINT verifica_salario CHECK (salario > 10000) NOT VALID;


/* 
d) Com base na tabela Jogador e Posicao_jogador:

i) Insira pelo menos duas tuplas em cada tabela 
iii) remova da tabela Jogador o atributo CPF, qual o efeito disso em Posicao_Jogador?
	R: Ao remover o atributo CPF da tabela Jogador, o efeito cascateia para posicao_jogador, oriundo da chave estrangeira
*/

-- i)
INSERT INTO jogador VALUES ('123456789-15', 'Cássio', 'Rua 14, n 28', 10000, 'Corinthians');
INSERT INTO jogador VALUES ('123456789-16', 'Bruno', 'Rua 28, n 56', 20000, 'Flamengo');

INSERT INTO posicao_jogador VALUES ('123456789-14', 'Atacante');
INSERT INTO posicao_jogador VALUES ('123456789-28', 'Goleiro');

--iii)
ALTER TABLE jogador DROP COLUMN cpf;

/* 
b) Faça o mesmo teste para um novo atributo qualquer com valor default. 
R: Como foi definido um valor "default" todos os jogadores receberão 0 na coluna salário em vez de NULL
*/

ALTER TABLE jogador ADD salario FLOAT DEFAULT 0;

/* 
c) escolha uma tabela e crie uma nova constraint do tipo check, de modo que os valores já existentes na 
tabela não atendam à nova restrição (faça as inserções necessárias para teste antes da criação da nova constraint). 

R: Ao efetuar a alteração da tabela jogador, é adicionada a constraint verifica_salario para todas as 
tuplas da tabela, porém como há tuplas que não atendem a condição, o que ocasiona ela ser invalidada, diferente do caso que se usa o NOT VALID, pois assim
a constraint n passa pelo processo de validação, e é inserida do msm jeito
*/

UPDATE jogador SET salario = 5000 WHERE cpf = '123456789-10';

UPDATE jogador SET salario = 9999 WHERE cpf = '123456789-11';

--nova constraint (invalidada)
ALTER TABLE jogador ADD CONSTRAINT verifica_salario CHECK (salario > 10000);

--nova constraint (não verificada, inserida)
ALTER TABLE jogador ADD CONSTRAINT verifica_salario CHECK (salario > 10000) NOT VALID;


/* 
d) Com base na tabela Jogador e Posicao_jogador:

i) Insira pelo menos duas tuplas em cada tabela 
iii) remova da tabela Jogador o atributo CPF, qual o efeito disso em Posicao_Jogador?
	R: Ao remover o atributo CPF da tabela Jogador, um erro ocorre, pois posicao_jogador depende desse atributo
*/

-- i)
INSERT INTO jogador VALUES ('123456789-15', '121212121', 'Cássio', '12/12/1983' , 'BRA', 'corinthians', 'Rua 14, n 28', 15000);
INSERT INTO jogador VALUES ('123456789-16', '212121212', 'Deola', '12/10/1983', 'BRA', 'Fluminense', 'Rua 28, n 56', 20000);

INSERT INTO posicao_jogador VALUES ('123456789-15', 'Goleiro');
INSERT INTO posicao_jogador VALUES ('123456789-16', 'Goleiro');

--iii)
ALTER TABLE jogador DROP COLUMN cpf;
