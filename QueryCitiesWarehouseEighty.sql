SELECT 
    city, 
    COUNT(*) AS warehouse_count
FROM warehouses
WHERE 
    date_open <= CURRENT_DATE
    AND (date_close IS NULL OR date_close > CURRENT_DATE)
GROUP BY city
HAVING COUNT(*) > 80;