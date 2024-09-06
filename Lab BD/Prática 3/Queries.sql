--1. (1.0) Inserção de dados
--Insira 5 tuplas em cada entidade como descrito no diagrama entidade-relacionamento e 20 tuplas para cada
--relação decorrente de relacionamento N:N. Insira dados consistentes para uso posterior.
  
--2. Selecione os seguintes dados:
  
--a) (0.5) Quais disputas irão ocorrer em uma data específica (data, horário, local, modalidade)?
SELECT DATA_HORA, LOCAL, ESPORTE
FROM DISPUTA, MODALIDADE
where trunc(DATA_HORA) = TO_DATE('2016-08-20','YYYY-MM-DD');

--b) (0.5) Quais são os locais de competição e qual é a agenda de eventos para cada local?
SELECT LOCAL.NOME, disputa.data_hora
FROM LOCAL, DISPUTA
WHERE LOCAL.ID = DISPUTA.LOCAL
ORDER BY LOCAL.ID;

--c) (0.5) Quanto é o ganho de patrocínio de cada atleta em cada ano?
SELECT NOME, SUM(VALOR_TOTAL)
FROM ATLETA, PATROCINA
WHERE ATLETA.PASSAPORTE = PATROCINA.ATLETA
GROUP BY NOME
ORDER BY SUM(VALOR_TOTAL);
  
--d) (0.5) Em quais mídias ocorrerá a transmissão de uma dada modalidade esportiva? Qual é a agenda de transmissões para uma dada modalidade?
SELECT m.NOME, m.TIPO, d.DATA_HORA
    FROM MIDIA m
    JOIN TRANSMITE t ON m.ID = t.MIDIA
    JOIN DISPUTA d ON t.DISPUTA = d.ID
    WHERE d.MODALIDADE = 1;

SELECT o.ANO, o.PAIS, o.CIDADE_SEDE, d.DATA_HORA, md.ESPORTE, md.GENERO, m.NOME AS MIDIA, m.TIPO AS TIPO_MIDIA
    FROM L05_DISPUTA d
    JOIN L11_TRANSMITE t ON d.ID = t.DISPUTA
    JOIN L10_MIDIA m ON t.MIDIA = m.ID
    JOIN OLIMPIADA o ON o.ANO = d.OLIMPIADA
    JOIN MODALIDADE md ON md.ID = d.MODALIDADE
    WHERE d.MODALIDADE = 1
ORDER BY d.DATA_HORA;

--e) (0.5) Compute o número total de disputas que ocorreram em cada local, para cada modalidade, durante uma determinada Olimpíada.
SELECT L.NOME AS LOCAL, M.ESPORTE AS MODALIDADE, D.OLIMPIADA AS ANO, COUNT(D.ID) AS TOTAL_DISPUTAS FROM DISPUTA D
    JOIN LOCAL L ON L.ID = D.LOCAL
    JOIN MODALIDADE M ON M.ID = D.MODALIDADE
    WHERE D.OLIMPIADA = 2016
    GROUP BY L.NOME, M.ESPORTE, D.OLIMPIADA
    ORDER BY L.NOME, M.ESPORTE;
  
--f) (0.5) Compute a média de capacidade dos locais por tipo de local e continente dos países onde ocorreram as Olimpíadas.
SELECT L.TIPO, P.CONTINENTE, AVG(L.CAPACIDADE) AS CAPACIDADE_MEDIA FROM DISPUTA D
    JOIN LOCAL L ON L.ID = D.LOCAL
    JOIN PAIS P ON P.NOME = L.PAIS
    WHERE D.OLIMPIADA = 2016
    GROUP BY L.TIPO, P.CONTINENTE
    ORDER BY L.TIPO, P.CONTINENTE;
  
--g) (1.0) Reporte quais são os atletas que participaram do maior número de disputas em toda a história de olimpiadas.
SELECT A.NOME, A.PAIS, COUNT(J.DISPUTA) AS NUM_DISPUTAS FROM ATLETA A
JOIN JOGA J ON A.PASSAPORTE = J.ATLETA
GROUP BY A.NOME, A.PAIS
ORDER BY NUM_DISPUTAS DESC;
  
--h) (1.0) Qual foi a sequência de resultados de uma dada modalidade em um dado ano? Indique o número de vitórias de cada país, ordene e ranqueie os mais vitoriosos – use função analítica.
SELECT
    D.PAIS1, D.PAIS2, D.VENCEDOR, O.ANO, M.ESPORTE, VIT.VITORIAS,
    DENSE_RANK() OVER (PARTITION BY O.ANO, M.ESPORTE ORDER BY VIT.VITORIAS DESC) AS RANKING
FROM DISPUTA D
    JOIN OLIMPIADA O ON D.OLIMPIADA = O.ANO
    JOIN MODALIDADE M ON M.ID = D.MODALIDADE
    JOIN (
        SELECT D1.VENCEDOR AS PAIS, COUNT(*) AS VITORIAS FROM DISPUTA D1
            GROUP BY D1.VENCEDOR
         )VIT ON D.VENCEDOR = VIT.PAIS
    WHERE O.ANO = 2016 AND M.ESPORTE = 'Atletismo'
    ORDER BY RANKING DESC;
  
--i) (1.0) Calcule o valor acumulado dos patrocínios recebidos por cada atleta ao longo dos anos, indicando o
--nome do atleta, e o seu ranking de acordo com o valor acumulado.
SELECT
    A.NOME AS ATLETA,
    SUM(PA.VALOR_TOTAL) AS VALOR_ACUMULADO,
    RANK() OVER (ORDER BY SUM(PA.VALOR_TOTAL) DESC) AS RANKING
FROM
    PATROCINADOR PR
    JOIN PATROCINA PA ON PR.ID = PA.PATROCINADOR
    JOIN ATLETA A ON A.PASSAPORTE = PA.ATLETA
GROUP BY
    A.NOME
ORDER BY
    VALOR_ACUMULADO DESC;
  
--j) (1.0) Conte o número de vitórias e derrotas por país em cada modalidade de cada olímpiada.
SELECT ESPORTE, ANO, PAIS, SUM(VITORIAS) AS VITORIAS, SUM(DERROTAS) AS DERROTAS
    FROM (
        SELECT M.ESPORTE, O.ANO, D.PAIS1 AS PAIS,
            COUNT(CASE WHEN D.VENCEDOR = D.PAIS1 THEN 1 END) AS VITORIAS,
            COUNT(CASE WHEN D.VENCEDOR = D.PAIS2 THEN 1 END) AS DERROTAS 
        FROM DISPUTA D
            JOIN MODALIDADE M ON M.ID = D.MODALIDADE
            JOIN OLIMPIADA O ON O.ANO = D.OLIMPIADA
GROUP BY M.ESPORTE, O.ANO, D.PAIS1

UNION ALL

SELECT M.ESPORTE, O.ANO, D.PAIS2 AS PAIS,
    COUNT(CASE WHEN D.VENCEDOR = D.PAIS2 THEN 1 END) AS VITORIAS,
    COUNT(CASE WHEN D.VENCEDOR = D.PAIS1 THEN 1 END) AS DERROTAS
FROM DISPUTA D
    JOIN MODALIDADE M ON M.ID = D.MODALIDADE
    JOIN OLIMPIADA O ON O.ANO = D.OLIMPIADA
    GROUP BY M.ESPORTE, O.ANO, D.PAIS2
) 
GROUP BY ESPORTE, ANO, PAIS
ORDER BY ANO, ESPORTE, PAIS;
  
-- 3. (2.0) Considere a seguinte tarefa: selecionar todos os eventos que alguma vez já tiveram disputas em locais com capacidade maior do que 50.000 pessoas.
-- - Implemente 3 versões para esta consulta:

--a) versão 1: apenas usando junção
SELECT D.PAIS1, D.PAIS2, D.VENCEDOR, D.OLIMPIADA AS ANO, D.DATA_HORA, M.ESPORTE, M.GENERO, O.PAIS, O.CIDADE_SEDE, L.NOME FROM DISPUTA D
    JOIN MODALIDADE M ON M.ID = D.MODALIDADE
    JOIN OLIMPIADA O ON O.ANO = D.OLIMPIADA
    JOIN LOCAL L ON L.ID = D.LOCAL
    WHERE L.CAPACIDADE > 50000

--b) versão 2: com consultas aninhadas correlacionadas (EXISTS)
SELECT D.PAIS1, D.PAIS2, D.VENCEDOR, D.OLIMPIADA AS ANO, D.DATA_HORA, M.ESPORTE, M.GENERO, O.PAIS, O.CIDADE_SEDE, L.NOME
FROM DISPUTA D
JOIN MODALIDADE M ON M.ID = D.MODALIDADE
JOIN OLIMPIADA O ON O.ANO = D.OLIMPIADA
JOIN LOCAL L ON L.ID = D.LOCAL
WHERE EXISTS (
    SELECT 1
    FROM LOCAL
    WHERE ID = D.LOCAL
    AND CAPACIDADE > 50000
);

--c) versão 3: com consultas aninhadas não correlacionadas (IN)
SELECT D.PAIS1, D.PAIS2, D.VENCEDOR, D.OLIMPIADA AS ANO, D.DATA_HORA, M.ESPORTE, M.GENERO, O.PAIS, O.CIDADE_SEDE, L.NOME FROM DISPUTA D
JOIN MODALIDADE M ON M.ID = D.MODALIDADE
JOIN OLIMPIADA O ON O.ANO = D.OLIMPIADA
JOIN LOCAL L ON L.ID = D.LOCAL
WHERE D.LOCAL IN (
    SELECT ID
    FROM LOCAL
    WHERE CAPACIDADE > 50000
