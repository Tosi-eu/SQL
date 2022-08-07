SELECT TOP(100) * FROM FactSales
 ORDER BY SalesAmount DESC

SELECT TOP(10) * FROM DimProduct
 ORDER BY UnitPrice DESC, Weight DESC, AvailableForSaleDate ASC

SELECT ProductName AS 'Produto', Weight AS 'Peso'
	FROM DimProduct
	WHERE Weight > 100 ORDER BY Weight DESC

SELECT 

StoreName AS 'Nome da loja',
OpenDate AS 'Inaugurou em:',
EmployeeCount AS 'Funcionários' 

FROM DimStore 

WHERE CloseDate IS NULL AND Status = 'On'

SELECT *
FROM DimProduct
WHERE BrandName = 'Litware' AND ProductName LIKE '%Home Theater%' AND StopSaleDate IS NULL AND AvailableForSaleDate = '20090315'


SELECT * FROM DimStore
	WHERE Status = 'Off' OR CloseDate IS NOT NULL

SELECT * FROM DimStore
	WHERE EmployeeCount BETWEEN 1 AND 20

SELECT 

 ProductName AS 'Nome do Produto',
 UnitPrice AS 'Preço unitário',
 ProductKey AS 'ID',
 ProductLabel AS 'Código do Produto'

FROM DimProduct
 WHERE ProductName LIKE '%LCD%'

 SELECT * FROM DimProduct
	WHERE ColorName IN ('Green', 'Orange', 'Black', 'Silver', 'Pink') AND BrandName IN ('Contoso', 'Litware', 'Fabrikam')

SELECT 

ProductName AS 'Nome do Produto',
ProductKey AS 'ID do Produto',
BrandName AS 'Fabricante',
UnitPrice AS 'Preço do Produto'

FROM DimProduct
	WHERE BrandName = 'Contoso' AND ColorName = 'Silver' AND UnitPrice BETWEEN 10 AND 30 AND StopSaleDate IS NULL
	ORDER BY UnitPrice DESC
