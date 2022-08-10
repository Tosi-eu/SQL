SELECT
	channelKey AS 'ChannelKey',
	SUM(SalesQuantity) AS 'Sales Amount'

FROM FactSales
GROUP BY channelKey

SELECT 
	StoreKey AS 'Store ID',
	SUM(SalesQuantity) AS 'Sales Amount',
	SUM(ReturnQuantity) AS 'Returned Amount'
FROM FactSales
GROUP BY StoreKey

SELECT
	channelKey,
	SUM(SalesAmount) AS 'Sales Amount'
FROM FactSales
WHERE DateKey BETWEEN '20070101' AND '20071231'
GROUP BY channelKey

SELECT
	ProductKey,
	SUM(SalesAmount) AS 'Sales Amount'
FROM FactSales
GROUP BY ProductKey
HAVING SUM(SalesAmount) >= 5000000.00
ORDER BY SUM(SalesAmount) DESC

SELECT
	TOP(10)
	ProductKey,
	SUM(SalesAmount) AS 'Sales Amount'
FROM FactSales
GROUP BY ProductKey
ORDER BY SUM(SalesAmount) DESC

SELECT 
	CustomerKey,
	SUM(SalesQuantity) AS 'Amount Sold'
FROM FactOnlineSales
GROUP BY CustomerKey
ORDER BY SUM(SalesQuantity) DESC

SELECT
	ProductKey AS 'Product ID',
	SUM(SalesQuantity) AS 'Amount Sold'
FROM FactOnlineSales
WHERE CustomerKey = 19037
GROUP BY ProductKey
ORDER BY SUM(SalesQuantity) DESC

SELECT 
	BrandName AS 'Brand Name',
	COUNT(BrandName) AS 'Prods. per Brand'
FROM DimProduct
GROUP BY BrandName

SELECT
	ClassName AS 'Class Names',
	AVG(UnitPrice) AS 'Class Mean'
FROM DimProduct
GROUP BY ClassName

SELECT
	ColorName AS 'Color Products Names',
	SUM(Weight) AS 'Product Weights'
FROM DimProduct
GROUP BY ColorName
ORDER BY SUM(Weight) DESC

SELECT 
	BrandName,
	COUNT(BrandName) AS 'Disponible Prods. per Brand'
FROM DimProduct
GROUP BY BrandName

SELECT
	ClassName,
	AVG(UnitPrice) AS 'Unitary Prices Mean'
FROM DimProduct
GROUP BY ClassName

SELECT 
	ColorName AS 'Product Colors Available',
	SUM(Weight) AS 'Total Weight per Product Color'
FROM DimProduct
GROUP BY ColorName

SELECT 
	BrandName AS 'Brand Name',
	COUNT(DISTINCT ColorName) AS 'Color Qtd. by Prod.'
FROM DimProduct WHERE BrandName = 'Contoso' --Select brandname as you want
GROUP BY BrandName

SELECT 
	Gender AS 'Gender Type',
	COUNT(Gender) AS 'People Gender Amonut',
	AVG(YearlyIncome) AS 'Annual Wage per Client'
FROM DimCustomer
WHERE Gender IS NOT NULL GROUP BY Gender 

-- Education + YearlyIncome
SELECT 
	Education AS 'Degree',
	COUNT(Education) AS 'Degree Type per Group of Clients',
	AVG(YearlyIncome) AS 'Annual Wage per Client Group'
FROM DimCustomer
WHERE Education IS NOT NULL GROUP BY Education

SELECT 
	DepartmentName AS 'Departments',
	COUNT(DepartmentName) AS 'People Amount Separated by Department'
FROM DimEmployee 
WHERE EndDate IS NULL OR Status IS NULL
GROUP BY DepartmentName

SELECT 
	Title AS 'Job Name',
	COUNT(Title) AS 'Amount of Women per Job Type',
	SUM(VacationHours) AS 'Vacation Hours'
FROM DimEmployee WHERE Gender = 'F' AND DepartmentName IN ('Production', 'Marketing', 'Engineering', 'Finance') AND HireDate BETWEEN '1999-01-01' AND '2000-12-31'
GROUP BY Title


