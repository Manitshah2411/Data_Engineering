CREATE TABLE IF NOT EXISTS warehouse.fact_customer_lifecycle AS
SELECT 
	o.customer_unique_id,
	MIN(o.order_purchase_timestamp) AS first_order_date,
	MAX(o.order_purchase_timestamp) AS last_order_date,
	COUNT(DISTINCT o.order_id) AS num_orders,
	SUM(oi.price) AS total_revenue,
	ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id),2) AS avg_order_value,
	MAX(o.order_purchase_timestamp)::DATE - MIN(o.order_purchase_timestamp)::DATE AS days_active,
	CASE WHEN
		MAX(o.order_purchase_timestamp)::DATE >= (CURRENT_DATE - INTERVAL '365 days') THEN TRUE
		ELSE FALSE
	END AS is_active
FROM warehouse.dim_customers AS c
JOIN warehouse.dim_orders AS o
ON c.customer_unique_id = o.customer_unique_id
JOIN warehouse.fact_order_items AS oi
ON oi.order_id = o.order_id
GROUP BY  o.customer_unique_id;

GRANT INSERT, SELECT, UPDATE, TRUNCATE ON TABLE warehouse.fact_customer_lifecycle TO manitkalpeshshah;
