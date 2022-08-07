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