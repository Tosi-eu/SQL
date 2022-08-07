SELECT 

	ProductKey AS 'ProdID',
	ProductName AS 'ProdName',
	UnitPrice AS 'ProdPrice'

FROM DimProduct 

WHERE BrandName = 'Contoso' AND ColorName = 'Silver' AND UnitPrice BETWEEN 10 AND 30 

ORDER BY UnitPrice DESC
