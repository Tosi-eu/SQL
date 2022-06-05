-- * -> Retrun all columns
SELECT 
		*
FROM
	DimCustomer

SELECT 
	StoreKey,
	StoreName,
	StorePhone
FROM
	DimStore

SELECT
	  *
FROM
	DimProduct

-- If you want to deal with percentage, use TOP PERCENT, and if you want to deal with n rows, use TOP(n) -> OBS: They work together too
SELECT DISTINCT
	   ProductName,
	   BrandName,
	   UnitCost,
	   UnitPrice
FROM
	DimProduct


SELECT
	  *
FROM
	DimEmployee

-- I want to search departments to be able to get a job, but in this case, departments columns have a lot of repeated values, so:
SELECT DISTINCT
			   DepartmentName 
							AS 
							  JobPossibilities

FROM
	DimEmployee

