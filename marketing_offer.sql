WITH order_summary AS (
    SELECT
        Customer_name,
        Order_Id,
        DATE_TRUNC('month', Order_day) AS month,
        MAX(CASE WHEN Prod_Name = 'iPhone' THEN 1 ELSE 0 END) AS has_iphone,
        MAX(CASE WHEN Prod_Name = 'Airpods' THEN 1 ELSE 0 END) AS has_airpods
    FROM orders
    GROUP BY Customer_name, Order_Id, DATE_TRUNC('month', Order_day)
)
SELECT
    month,
    COUNT(DISTINCT Customer_name) AS customer_count
FROM order_summary
WHERE has_iphone = 1 AND has_airpods = 0
GROUP BY month
ORDER BY month;