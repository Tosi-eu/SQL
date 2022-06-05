-- Exercise 2) --

SELECT

	CustomerKey AS "Unique ID",
	FirstName AS "Person Name",
	EmailAddress AS Email,
	BirthDate AS Birthday

FROM DimCustomer


-- exercise 3) --

SELECT
	TOP(100)
			FirstName AS "Nome do Cliente",
			EmailAddress AS "Email do Cliente",
			BirthDate AS "Data de Nascimento"

FROM
	DimCustomer

SELECT TOP(20) PERCENT
						*
FROM DimCustomer


-- Exercise 4)

SELECT DISTINCT
			   Manufacturer AS	
							 "Nome do Produtor"
							
FROM DimProduct


-- Exercise 5)

SELECT *

FROM DimProduct

SELECT DISTINCT ProductKey 

FROM FactSales

-- By the number of rows, fact sales has 2516 rows, and DimProduct has 2517, so one product wasn't sold or table is with dome problem
