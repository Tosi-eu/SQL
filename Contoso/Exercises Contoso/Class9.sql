SELECT * FROM FactSales

SELECT * FROM DimChannel

/* Products sold and the return of them */
SELECT 
	SUM(SalesQuantity) AS 'Qtd. ProdSold',
	SUM(ReturnQuantity) AS 'Qtd. Product'
FROM FactSales WHERE channelKey = 1


SELECT 
		AVG(YearlyIncome) AS 'Annual Wage Mean'
FROM DimCustomer WHERE Occupation = 'Professional'

SELECT 
	TOP(1) EmployeeCount AS 'Employees Qtd.',
	StoreName AS 'Store Name'
FROM DimStore
ORDER BY EmployeeCount DESC

SELECT 
	TOP(1) EmployeeCount AS 'Employees Qtd.',
	StoreName AS 'Store Name'
FROM DimStore 
WHERE EmployeeCount IS NOT NULL ORDER BY EmployeeCount ASC

SELECT
	COUNT(FirstName)
FROM DimEmployee WHERE Gender = 'M'

SELECT
	COUNT(FirstName)
FROM DimEmployee WHERE Gender = 'F'

SELECT * FROM DimEmployee

SELECT 
	TOP(1) HireDate,
	EmailAddress,
	FirstName,
	MiddleName,
	LastName
FROM DimEmployee WHERE Gender = 'M'
ORDER BY HireDate ASC

SELECT 
	TOP(1) HireDate,
	EmailAddress,
	FirstName,
	MiddleName,
	LastName
FROM DimEmployee WHERE Gender = 'F'
ORDER BY HireDate ASC

SELECT * FROM DimProduct

SELECT 
	COUNT(DISTINCT(ColorName)) AS 'Unique Colors Qtd.',
	COUNT(DISTINCT(BrandName)) AS 'Unique BrandNames Qtd.',
	Count(DISTINCT(ClassName)) AS 'Unique ClassNames Qtd.'
FROM DimProduct
