
CREATE TABLE IF NOT EXISTS warehouse.fact_product_performance AS
SELECT 
	p.product_id,
	p.product_category_name,
	COUNT(DISTINCT o.order_id) AS total_units_sold,
	SUM(oi.price) AS total_revenue,
	ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id),2) AS avg_selling_price,
	MIN(o.order_purchase_timestamp) AS first_sold_date,
	MAX(o.order_purchase_timestamp) AS last_sold_date
FROM warehouse.fact_order_items AS oi
JOIN warehouse.dim_products AS p
ON p.product_id = oi.product_id
JOIN warehouse.dim_orders AS o
ON o.order_id = oi.order_id
GROUP BY p.product_id,
	p.product_category_name


GRANT ALL PRIVILEGES ON TABLE warehouse.fact_product_performance TO manitkalpeshshah;

ALTER TABLE warehouse.fact_product_performance
ADD CONSTRAINT pk_fact_product_performance
PRIMARY KEY (product_id);

