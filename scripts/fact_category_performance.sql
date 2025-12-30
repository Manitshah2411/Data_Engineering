
CREATE TABLE IF NOT EXISTS warehouse.fact_category_performance AS
SELECT 
	p.product_category_name,
	SUM(oi.price) AS total_revenue,
	COUNT(DISTINCT o.order_id) AS total_units_sold, -- Also same as num_orders as here the quantity is always 1
	COUNT(DISTINCT p.product_id) AS num_products,
	ROUND(AVG(oi.price),2) AS avg_price
FROM warehouse.fact_order_items AS oi
JOIN warehouse.dim_orders AS o
ON o.order_id = oi.order_id
JOIN warehouse.dim_products AS p
ON p.product_id = oi.product_id
GROUP BY p.product_category_name;

GRANT ALL PRIVILEGES ON TABLE warehouse.fact_category_performance TO manitkalpeshshah;

ALTER TABLE warehouse.fact_category_performance
ADD CONSTRAINT pk_product_category_name
PRIMARY KEY (product_category_name);