
CREATE TABLE IF NOT EXISTS warehouse.fact_daily_sales AS
SELECT 
	DATE_TRUNC('day',o.order_purchase_timestamp) AS sales_date,
	SUM(fo.price) AS total_revenue,
	COUNT(DISTINCT o.order_id) AS total_order,
	COUNT(p.product_id) AS total_items,
	COUNT(DISTINCT c.customer_id) AS total_customers,
	ROUND(SUM(fo.price) / COUNT(DISTINCT o.order_id),2) AS avg_order_value
FROM warehouse.fact_order_items AS fo
JOIN warehouse.dim_orders AS o
ON fo.order_id = o.order_id
JOIN warehouse.dim_products AS p
ON p.product_id = fo.product_id
JOIN warehouse.dim_customers AS c
ON c.customer_unique_id = o.customer_unique_id
GROUP BY DATE_TRUNC('day',o.order_purchase_timestamp)
ORDER BY SUM(price) DESC;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA warehouse TO manitkalpeshshah;
GRANT USAGE ON SCHEMA warehouse TO manitkalpeshshah;

GRANT INSERT, SELECT, UPDATE, DELETE, TRUNCATE ON warehouse.fact_daily_sales TO manitkalpeshshah;



